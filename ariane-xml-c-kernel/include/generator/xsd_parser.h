#ifndef XSD_PARSER_H
#define XSD_PARSER_H

#include "xsd_schema.h"
#include <pugixml.hpp>
#include <string>
#include <memory>
#include <map>

namespace ariane_xml {

class XsdParser {
public:
    // Parse an XSD file and return the schema model
    static std::unique_ptr<XsdSchema> parse(const std::string& xsd_file_path);

private:
    // Store named types for lookup
    static std::map<std::string, std::shared_ptr<XsdElement>> named_types_;

    static std::shared_ptr<XsdElement> parseElement(
        const pugi::xml_node& node,
        const pugi::xml_document& doc
    );

    static std::shared_ptr<XsdElement> parseComplexType(
        const pugi::xml_node& complexTypeNode,
        const pugi::xml_document& doc
    );

    static std::shared_ptr<XsdElement> parseSequence(
        const pugi::xml_node& sequenceNode,
        const pugi::xml_document& doc
    );

    static void parseAndStoreNamedTypes(
        const pugi::xml_node& schemaNode,
        const pugi::xml_document& doc
    );

    static std::shared_ptr<XsdElement> createElementFromType(
        const std::string& typeName,
        const std::string& elementName
    );

    static XsdType parseType(const std::string& typeName);
    static int parseOccurs(const pugi::xml_node& node, const char* attrName, int defaultValue);
    static std::string stripNamespacePrefix(const std::string& name);
};

} // namespace ariane_xml

#endif // XSD_PARSER_H
