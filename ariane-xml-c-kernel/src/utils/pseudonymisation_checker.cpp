#include "utils/pseudonymisation_checker.h"
#include <pugixml.hpp>
#include <regex>
#include <iostream>

namespace ariane_xml {

bool PseudonymisationChecker::isPseudonymised(const std::string& filepath) {
    pugi::xml_document doc;
    // Must use parse_pi flag to read processing instructions
    pugi::xml_parse_result result = doc.load_file(filepath.c_str(), pugi::parse_default | pugi::parse_pi);

    if (!result) {
        return false;
    }

    // Look for processing instruction with our marker target
    for (pugi::xml_node child = doc.first_child(); child; child = child.next_sibling()) {
        if (child.type() == pugi::node_pi) {
            if (std::string(child.name()) == PSEUDO_MARKER_TARGET) {
                return true;
            }
        }
    }

    return false;
}

std::optional<PseudonymisationMetadata> PseudonymisationChecker::getMetadata(const std::string& filepath) {
    pugi::xml_document doc;
    // Must use parse_pi flag to read processing instructions
    pugi::xml_parse_result result = doc.load_file(filepath.c_str(), pugi::parse_default | pugi::parse_pi);

    if (!result) {
        return std::nullopt;
    }

    // Look for processing instruction with our marker target
    for (pugi::xml_node child = doc.first_child(); child; child = child.next_sibling()) {
        if (child.type() == pugi::node_pi) {
            if (std::string(child.name()) == PSEUDO_MARKER_TARGET) {
                // Parse the attributes from the PI value
                std::string piValue = child.value();
                PseudonymisationMetadata metadata;

                // Extract version
                std::regex versionRegex(R"regex(version="([^"]*)")regex");
                std::smatch versionMatch;
                if (std::regex_search(piValue, versionMatch, versionRegex)) {
                    metadata.version = versionMatch[1].str();
                }

                // Extract date
                std::regex dateRegex(R"regex(date="([^"]*)")regex");
                std::smatch dateMatch;
                if (std::regex_search(piValue, dateMatch, dateRegex)) {
                    metadata.date = dateMatch[1].str();
                }

                // Extract tool
                std::regex toolRegex(R"regex(tool="([^"]*)")regex");
                std::smatch toolMatch;
                if (std::regex_search(piValue, toolMatch, toolRegex)) {
                    metadata.tool = toolMatch[1].str();
                }

                // Extract config-hash
                std::regex hashRegex(R"regex(config-hash="([^"]*)")regex");
                std::smatch hashMatch;
                if (std::regex_search(piValue, hashMatch, hashRegex)) {
                    metadata.config_hash = hashMatch[1].str();
                }

                return metadata;
            }
        }
    }

    return std::nullopt;
}

std::string PseudonymisationChecker::formatMetadata(const PseudonymisationMetadata& metadata) {
    std::string result;
    result += "Pseudonymisation Information:\n";
    result += "  Version: " + metadata.version + "\n";
    result += "  Date: " + metadata.date + "\n";
    result += "  Tool: " + metadata.tool + "\n";
    result += "  Config Hash: " + metadata.config_hash;
    return result;
}

} // namespace ariane_xml
