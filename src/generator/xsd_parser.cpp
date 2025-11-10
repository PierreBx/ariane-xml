#include "generator/xsd_parser.h"
#include <iostream>
#include <algorithm>
#include <cstring>

namespace expocli {

// Initialize static member
std::map<std::string, std::shared_ptr<XsdElement>> XsdParser::named_types_;

std::unique_ptr<XsdSchema> XsdParser::parse(const std::string& xsd_file_path) {
    // Clear previous types
    named_types_.clear();

    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_file(xsd_file_path.c_str());

    if (!result) {
        throw std::runtime_error("Failed to parse XSD file: " + std::string(result.description()));
    }

    auto schema = std::make_unique<XsdSchema>();

    // Find the schema element (handle different namespace prefixes)
    pugi::xml_node schemaNode = doc.child("xs:schema");
    if (!schemaNode) {
        schemaNode = doc.child("xsd:schema");
    }
    if (!schemaNode) {
        schemaNode = doc.child("schema");
    }

    if (!schemaNode) {
        throw std::runtime_error("No schema element found in XSD file");
    }

    // Get target namespace if present
    const char* targetNs = schemaNode.attribute("targetNamespace").value();
    if (targetNs) {
        schema->setTargetNamespace(targetNs);
    }

    // First pass: parse and store all named types (complexType, simpleType)
    parseAndStoreNamedTypes(schemaNode, doc);

    // Find the root element (first xs:element)
    pugi::xml_node rootElementNode = schemaNode.child("xs:element");
    if (!rootElementNode) {
        rootElementNode = schemaNode.child("xsd:element");
    }
    if (!rootElementNode) {
        rootElementNode = schemaNode.child("element");
    }

    std::shared_ptr<XsdElement> rootElement;

    if (rootElementNode) {
        // Found explicit root element
        rootElement = parseElement(rootElementNode, doc);
    } else {
        // No explicit root element - find first complexType (not simpleType)
        if (named_types_.empty()) {
            throw std::runtime_error("No root element or named types found in XSD schema");
        }

        // Find the first complex type (skip simple types)
        std::string rootTypeName;
        for (const auto& [name, element] : named_types_) {
            if (element->type == XsdType::COMPLEX) {
                rootTypeName = name;
                break;
            }
        }

        if (rootTypeName.empty()) {
            // No complex types found, fall back to first type
            rootTypeName = named_types_.begin()->first;
        }

        std::cout << "No root element found. Using first complexType as root: "
                  << rootTypeName << std::endl;

        rootElement = createElementFromType(rootTypeName, rootTypeName);
    }

    schema->setRootElement(rootElement);

    return schema;
}

std::shared_ptr<XsdElement> XsdParser::parseElement(
    const pugi::xml_node& node,
    const pugi::xml_document& doc
) {
    auto element = std::make_shared<XsdElement>();

    // Get element name
    const char* name = node.attribute("name").value();
    if (name) {
        element->name = name;
    }

    // Get minOccurs and maxOccurs
    element->minOccurs = parseOccurs(node, "minOccurs", 1);
    element->maxOccurs = parseOccurs(node, "maxOccurs", 1);

    // Check for type reference
    const char* typeName = node.attribute("type").value();
    if (typeName && strlen(typeName) > 0) {
        // Strip namespace prefix and look up the type
        std::string cleanTypeName = stripNamespacePrefix(typeName);

        auto it = named_types_.find(cleanTypeName);
        if (it != named_types_.end()) {
            // Reference to a named type - copy its structure
            element->type = it->second->type;
            element->children = it->second->children;
            element->attributes = it->second->attributes;
        } else {
            // Built-in type (string, int, etc.)
            element->type = parseType(typeName);
        }
    }

    // Check for inline complex type (overrides type attribute)
    pugi::xml_node complexTypeNode = node.child("xs:complexType");
    if (!complexTypeNode) {
        complexTypeNode = node.child("xsd:complexType");
    }
    if (!complexTypeNode) {
        complexTypeNode = node.child("complexType");
    }

    if (complexTypeNode) {
        element->type = XsdType::COMPLEX;
        auto complexElement = parseComplexType(complexTypeNode, doc);
        element->children = complexElement->children;
        element->attributes = complexElement->attributes;
    }

    return element;
}

std::shared_ptr<XsdElement> XsdParser::parseComplexType(
    const pugi::xml_node& complexTypeNode,
    const pugi::xml_document& doc
) {
    auto element = std::make_shared<XsdElement>();
    element->type = XsdType::COMPLEX;

    // Check for complexContent with extension (inheritance)
    pugi::xml_node complexContentNode = complexTypeNode.child("xs:complexContent");
    if (!complexContentNode) {
        complexContentNode = complexTypeNode.child("xsd:complexContent");
    }
    if (!complexContentNode) {
        complexContentNode = complexTypeNode.child("complexContent");
    }

    if (complexContentNode) {
        // Handle extension
        pugi::xml_node extensionNode = complexContentNode.child("xs:extension");
        if (!extensionNode) {
            extensionNode = complexContentNode.child("xsd:extension");
        }
        if (!extensionNode) {
            extensionNode = complexContentNode.child("extension");
        }

        if (extensionNode) {
            // Get base type and merge its structure
            const char* baseType = extensionNode.attribute("base").value();
            if (baseType && strlen(baseType) > 0) {
                std::string cleanBaseType = stripNamespacePrefix(baseType);
                auto it = named_types_.find(cleanBaseType);
                if (it != named_types_.end()) {
                    // Copy base type's children and attributes
                    element->children = it->second->children;
                    element->attributes = it->second->attributes;
                }
            }

            // Parse extension's sequence (additional children)
            pugi::xml_node extSequenceNode = extensionNode.child("xs:sequence");
            if (!extSequenceNode) {
                extSequenceNode = extensionNode.child("xsd:sequence");
            }
            if (!extSequenceNode) {
                extSequenceNode = extensionNode.child("sequence");
            }

            if (extSequenceNode) {
                auto sequenceElement = parseSequence(extSequenceNode, doc);
                // Append to existing children from base type
                element->children.insert(element->children.end(),
                                        sequenceElement->children.begin(),
                                        sequenceElement->children.end());
            }

            // Parse extension's attributes (additional attributes)
            for (const char* prefix : {"xs:", "xsd:", ""}) {
                std::string attrTag = std::string(prefix) + "attribute";
                for (pugi::xml_node attrNode : extensionNode.children(attrTag.c_str())) {
                    auto attr = std::make_shared<XsdElement>();
                    attr->isAttribute = true;
                    attr->name = attrNode.attribute("name").value();

                    const char* attrType = attrNode.attribute("type").value();
                    if (attrType) {
                        attr->type = parseType(attrType);
                    } else {
                        attr->type = XsdType::STRING;
                    }

                    element->attributes.push_back(attr);
                }
            }
        }
    } else {
        // Regular complexType without extension

        // Look for sequence
        pugi::xml_node sequenceNode = complexTypeNode.child("xs:sequence");
        if (!sequenceNode) {
            sequenceNode = complexTypeNode.child("xsd:sequence");
        }
        if (!sequenceNode) {
            sequenceNode = complexTypeNode.child("sequence");
        }

        if (sequenceNode) {
            auto sequenceElement = parseSequence(sequenceNode, doc);
            element->children = sequenceElement->children;
        }

        // Parse attributes
        for (const char* prefix : {"xs:", "xsd:", ""}) {
            std::string attrTag = std::string(prefix) + "attribute";
            for (pugi::xml_node attrNode : complexTypeNode.children(attrTag.c_str())) {
                auto attr = std::make_shared<XsdElement>();
                attr->isAttribute = true;
                attr->name = attrNode.attribute("name").value();

                const char* attrType = attrNode.attribute("type").value();
                if (attrType) {
                    attr->type = parseType(attrType);
                } else {
                    attr->type = XsdType::STRING;
                }

                element->attributes.push_back(attr);
            }
        }
    }

    return element;
}

std::shared_ptr<XsdElement> XsdParser::parseSequence(
    const pugi::xml_node& sequenceNode,
    const pugi::xml_document& doc
) {
    auto element = std::make_shared<XsdElement>();

    // Parse all child elements in the sequence
    for (pugi::xml_node childNode : sequenceNode.children()) {
        std::string nodeName = childNode.name();

        if (nodeName == "xs:element" || nodeName == "xsd:element" || nodeName == "element") {
            auto childElement = parseElement(childNode, doc);
            element->children.push_back(childElement);
        }
    }

    return element;
}

XsdType XsdParser::parseType(const std::string& typeName) {
    // Remove namespace prefix if present
    std::string cleanType = typeName;
    size_t colonPos = cleanType.find(':');
    if (colonPos != std::string::npos) {
        cleanType = cleanType.substr(colonPos + 1);
    }

    // Map XSD types to our internal types
    if (cleanType == "string") return XsdType::STRING;
    if (cleanType == "int" || cleanType == "integer" || cleanType == "long" || cleanType == "short") {
        return XsdType::INTEGER;
    }
    if (cleanType == "decimal" || cleanType == "float" || cleanType == "double") {
        return XsdType::DECIMAL;
    }
    if (cleanType == "boolean") return XsdType::BOOLEAN;
    if (cleanType == "date") return XsdType::DATE;
    if (cleanType == "dateTime") return XsdType::DATETIME;

    // Default to string for unknown types
    return XsdType::STRING;
}

int XsdParser::parseOccurs(const pugi::xml_node& node, const char* attrName, int defaultValue) {
    const char* value = node.attribute(attrName).value();

    if (!value || strlen(value) == 0) {
        return defaultValue;
    }

    std::string strValue = value;

    if (strValue == "unbounded") {
        return -1;  // -1 represents unbounded
    }

    try {
        return std::stoi(strValue);
    } catch (...) {
        return defaultValue;
    }
}

std::string XsdParser::stripNamespacePrefix(const std::string& name) {
    size_t colonPos = name.find(':');
    if (colonPos != std::string::npos) {
        return name.substr(colonPos + 1);
    }
    return name;
}

void XsdParser::parseAndStoreNamedTypes(
    const pugi::xml_node& schemaNode,
    const pugi::xml_document& doc
) {
    // Parse all complexType definitions
    for (const char* prefix : {"xs:", "xsd:", ""}) {
        std::string complexTypeTag = std::string(prefix) + "complexType";

        for (pugi::xml_node typeNode : schemaNode.children(complexTypeTag.c_str())) {
            const char* typeName = typeNode.attribute("name").value();
            if (typeName && strlen(typeName) > 0) {
                auto element = parseComplexType(typeNode, doc);
                element->name = typeName;
                named_types_[typeName] = element;
            }
        }
    }

    // Parse all simpleType definitions (enumerations, restrictions)
    for (const char* prefix : {"xs:", "xsd:", ""}) {
        std::string simpleTypeTag = std::string(prefix) + "simpleType";

        for (pugi::xml_node typeNode : schemaNode.children(simpleTypeTag.c_str())) {
            const char* typeName = typeNode.attribute("name").value();
            if (typeName && strlen(typeName) > 0) {
                // For now, treat simple types as strings
                // Could be enhanced to parse restrictions/enumerations
                auto element = std::make_shared<XsdElement>();
                element->name = typeName;
                element->type = XsdType::STRING;
                named_types_[typeName] = element;
            }
        }
    }
}

std::shared_ptr<XsdElement> XsdParser::createElementFromType(
    const std::string& typeName,
    const std::string& elementName
) {
    // Strip namespace prefix from type name
    std::string cleanTypeName = stripNamespacePrefix(typeName);

    // Look up the type
    auto it = named_types_.find(cleanTypeName);
    if (it != named_types_.end()) {
        // Clone the type definition
        auto element = std::make_shared<XsdElement>();
        element->name = elementName;
        element->type = it->second->type;
        element->children = it->second->children;
        element->attributes = it->second->attributes;
        element->minOccurs = 1;
        element->maxOccurs = 1;
        return element;
    }

    // Type not found - return a simple string element
    auto element = std::make_shared<XsdElement>();
    element->name = elementName;
    element->type = XsdType::STRING;
    return element;
}

} // namespace expocli
