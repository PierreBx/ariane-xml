#include "dsn/dsn_parser.h"
#include <pugixml.hpp>
#include <iostream>
#include <filesystem>
#include <regex>

namespace ariane_xml {

std::shared_ptr<DsnSchema> DsnParser::parse(const std::string& xsdPath, const std::string& version) {
    auto schema = std::make_shared<DsnSchema>(version);

    // Load XSD file
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_file(xsdPath.c_str());

    if (!result) {
        std::cerr << "Error loading DSN XSD: " << result.description() << std::endl;
        return schema;
    }

    // Parse the XSD schema
    pugi::xml_node schemaNode = doc.child("xs:schema");
    if (!schemaNode) {
        schemaNode = doc.child("xsd:schema");
    }
    if (!schemaNode) {
        schemaNode = doc.child("schema");
    }

    if (!schemaNode) {
        std::cerr << "Error: No schema node found in XSD" << std::endl;
        return schema;
    }

    // Extract attributes from all elements
    for (pugi::xml_node node : schemaNode.children()) {
        std::string nodeName = node.name();

        if (nodeName == "xs:element" || nodeName == "xsd:element" || nodeName == "element") {
            parseElement(&node, *schema);
        } else if (nodeName == "xs:complexType" || nodeName == "xsd:complexType" || nodeName == "complexType") {
            parseComplexType(&node, *schema);
        }
    }

    return schema;
}

std::shared_ptr<DsnSchema> DsnParser::parseDirectory(const std::string& schemaDir, const std::string& version) {
    auto schema = std::make_shared<DsnSchema>(version);

    if (!std::filesystem::exists(schemaDir) || !std::filesystem::is_directory(schemaDir)) {
        std::cerr << "Error: Schema directory does not exist: " << schemaDir << std::endl;
        return schema;
    }

    // Parse all XSD files in the directory
    for (const auto& entry : std::filesystem::directory_iterator(schemaDir)) {
        if (entry.path().extension() == ".xsd") {
            std::string xsdPath = entry.path().string();
            std::cerr << "Parsing DSN schema: " << xsdPath << std::endl;

            // Load and parse this XSD file
            pugi::xml_document doc;
            pugi::xml_parse_result result = doc.load_file(xsdPath.c_str());

            if (!result) {
                std::cerr << "  Warning: Could not parse " << xsdPath << std::endl;
                continue;
            }

            pugi::xml_node schemaNode = doc.child("xs:schema");
            if (!schemaNode) schemaNode = doc.child("xsd:schema");
            if (!schemaNode) schemaNode = doc.child("schema");

            if (!schemaNode) {
                continue;
            }

            // Parse elements
            for (pugi::xml_node node : schemaNode.children()) {
                std::string nodeName = node.name();

                if (nodeName == "xs:element" || nodeName == "xsd:element" || nodeName == "element") {
                    parseElement(&node, *schema);
                } else if (nodeName == "xs:complexType" || nodeName == "xsd:complexType" || nodeName == "complexType") {
                    parseComplexType(&node, *schema);
                }
            }
        }
    }

    return schema;
}

std::string DsnParser::detectVersion(const std::string& xmlPath) {
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_file(xmlPath.c_str());

    if (!result) {
        return "";
    }

    // Look for version in S10_G00_00_006 field
    // Traverse the entire tree looking for this element
    pugi::xml_node versionNode = doc.find_node([](pugi::xml_node node) {
        return std::string(node.name()) == "S10_G00_00_006";
    });

    if (versionNode) {
        std::string versionValue = versionNode.text().as_string();
        if (versionValue.find("P25") != std::string::npos) {
            return "P25";
        } else if (versionValue.find("P26") != std::string::npos) {
            return "P26";
        }
    }

    return "";
}

std::string DsnParser::extractShortId(const std::string& full_name) {
    // Extract YY_ZZZ from SWW_GXX_YY_ZZZ
    // Example: S21_G00_30_001 -> 30_001

    std::regex pattern(R"(S\d+_G\d+_(\d+_\d+))");
    std::smatch match;

    if (std::regex_search(full_name, match, pattern)) {
        return match[1].str();
    }

    return "";
}

std::string DsnParser::extractBlocName(const std::string& full_name) {
    // Extract bloc name from attribute name
    // Example: S21_G00_30_001 -> S21.G00.30

    std::regex pattern(R"((S\d+)_(G\d+)_(\d+)_\d+)");
    std::smatch match;

    if (std::regex_search(full_name, match, pattern)) {
        return match[1].str() + "." + match[2].str() + "." + match[3].str();
    }

    return "";
}

std::string DsnParser::extractDescription(const std::string& documentation) {
    // Remove leading/trailing whitespace and newlines
    std::string desc = documentation;
    desc.erase(0, desc.find_first_not_of(" \t\n\r"));
    desc.erase(desc.find_last_not_of(" \t\n\r") + 1);
    return desc;
}

void DsnParser::parseElement(void* element, DsnSchema& schema) {
    pugi::xml_node* node = static_cast<pugi::xml_node*>(element);

    std::string elementName = node->attribute("name").as_string();

    // Only process DSN-style element names (S\d+_G\d+_\d+_\d+)
    std::regex dsnPattern(R"(S\d+_G\d+_\d+_\d+)");
    if (!std::regex_match(elementName, dsnPattern)) {
        return;
    }

    // Create DSN attribute
    DsnAttribute attr;
    attr.full_name = elementName;
    attr.short_id = extractShortId(elementName);
    attr.bloc_name = extractBlocName(elementName);

    // Extract type
    attr.type = node->attribute("type").as_string();

    // Extract occurrences
    std::string minOccurs = node->attribute("minOccurs").as_string("1");
    std::string maxOccurs = node->attribute("maxOccurs").as_string("1");

    attr.min_occurs = (minOccurs == "unbounded") ? -1 : std::stoi(minOccurs);
    attr.max_occurs = (maxOccurs == "unbounded") ? -1 : std::stoi(maxOccurs);
    attr.mandatory = (attr.min_occurs > 0);

    // Extract documentation
    pugi::xml_node annotation = node->child("xs:annotation");
    if (!annotation) annotation = node->child("xsd:annotation");
    if (!annotation) annotation = node->child("annotation");

    if (annotation) {
        pugi::xml_node documentation = annotation.child("xs:documentation");
        if (!documentation) documentation = annotation.child("xsd:documentation");
        if (!documentation) documentation = annotation.child("documentation");

        if (documentation) {
            attr.description = extractDescription(documentation.text().as_string());
        }
    }

    // Add to schema
    schema.addAttribute(attr);
}

void DsnParser::parseComplexType(void* complexType, DsnSchema& schema) {
    pugi::xml_node* node = static_cast<pugi::xml_node*>(complexType);

    // Recursively parse sequence/choice/all children
    for (pugi::xml_node child : node->children()) {
        std::string childName = child.name();

        if (childName == "xs:sequence" || childName == "xsd:sequence" || childName == "sequence") {
            for (pugi::xml_node element : child.children("xs:element")) {
                parseElement(&element, schema);
            }
            for (pugi::xml_node element : child.children("xsd:element")) {
                parseElement(&element, schema);
            }
            for (pugi::xml_node element : child.children("element")) {
                parseElement(&element, schema);
            }
        }
    }
}

} // namespace ariane_xml
