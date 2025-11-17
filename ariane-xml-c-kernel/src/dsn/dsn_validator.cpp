#include "dsn/dsn_validator.h"
#include <pugixml.hpp>
#include <regex>
#include <iostream>
#include <functional>

namespace ariane_xml {

DsnValidator::DsnValidator(std::shared_ptr<DsnSchema> schema)
    : schema_(schema) {}

DsnValidationResult DsnValidator::validate(const std::string& xmlPath) {
    DsnValidationResult result;

    // Load XML file
    pugi::xml_document doc;
    pugi::xml_parse_result parseResult = doc.load_file(xmlPath.c_str());

    if (!parseResult) {
        DsnValidationError error;
        error.type = "XML_PARSE_ERROR";
        error.message = "Failed to parse XML file: " + std::string(parseResult.description());
        error.path = xmlPath;
        result.errors.push_back(error);
        result.isValid = false;
        return result;
    }

    // Perform DSN-specific validations
    checkVersionCoherence(&doc, result);
    checkMandatoryBlocs(&doc, result);
    validateFieldFormats(&doc, result);

    result.isValid = result.errors.empty();
    return result;
}

bool DsnValidator::validateSiret(const std::string& siret, DsnValidationError& error) {
    // SIRET format: 14 digits (9 SIREN + 5 NIC)
    std::regex siretPattern(R"(^\d{14}$)");

    if (!std::regex_match(siret, siretPattern)) {
        error.type = "SIRET_FORMAT";
        error.message = "Invalid SIRET format (expected 14 digits)";
        error.value = siret;
        return false;
    }

    // TODO: Add Luhn algorithm checksum validation if needed

    return true;
}

bool DsnValidator::validateNir(const std::string& nir, DsnValidationError& error) {
    // NIR format: 15 digits (13 + 2 checksum) or 15 alphanumeric
    std::regex nirPattern(R"(^[0-9A-Z]{15}$)");

    if (!std::regex_match(nir, nirPattern)) {
        error.type = "NIR_FORMAT";
        error.message = "Invalid NIR format (expected 15 characters)";
        error.value = nir;
        return false;
    }

    // TODO: Add NIR checksum validation if needed

    return true;
}

bool DsnValidator::validateDate(const std::string& date, DsnValidationError& error) {
    // Date formats: JJMMAAAA or AAAAMMJJ (8 digits)
    std::regex datePattern(R"(^\d{8}$)");

    if (!std::regex_match(date, datePattern)) {
        error.type = "DATE_FORMAT";
        error.message = "Invalid date format (expected 8 digits)";
        error.value = date;
        return false;
    }

    // TODO: Add more sophisticated date validation (check valid day/month)

    return true;
}

void DsnValidator::checkMandatoryBlocs(void* xmlDoc, DsnValidationResult& result) {
    pugi::xml_document* doc = static_cast<pugi::xml_document*>(xmlDoc);

    // Check for mandatory DSN blocs
    std::vector<std::string> mandatoryBlocs = {
        "S10_G00_00",  // ENVOI
        "S10_G00_01",  // EMETTEUR
        "S20_G00_05",  // DSN_MENSUELLE or similar
        "S21_G00_06"   // ENTREPRISE
    };

    for (const auto& blocName : mandatoryBlocs) {
        std::string searchName = blocName;
        // Convert to tag name format
        pugi::xml_node node = doc->find_node([&searchName](pugi::xml_node n) {
            return std::string(n.name()) == searchName;
        });

        if (!node) {
            DsnValidationError error;
            error.type = "MANDATORY_BLOC_MISSING";
            error.message = "Mandatory bloc missing: " + blocName;
            error.field = blocName;
            result.errors.push_back(error);
        }
    }
}

void DsnValidator::checkVersionCoherence(void* xmlDoc, DsnValidationResult& result) {
    pugi::xml_document* doc = static_cast<pugi::xml_document*>(xmlDoc);

    // Find version field S10_G00_00_006
    pugi::xml_node versionNode = doc->find_node([](pugi::xml_node node) {
        return std::string(node.name()) == "S10_G00_00_006";
    });

    if (!versionNode) {
        result.warnings.push_back("Warning: Version field S10_G00_00_006 not found");
        return;
    }

    std::string declaredVersion = versionNode.text().as_string();

    // Check if declared version matches schema version
    if (schema_ && !declaredVersion.empty()) {
        std::string schemaVersion = schema_->getVersion();
        if (!schemaVersion.empty() &&
            declaredVersion.find(schemaVersion) == std::string::npos) {
            result.warnings.push_back(
                "Warning: Declared version (" + declaredVersion +
                ") does not match schema version (" + schemaVersion + ")"
            );
        }
    }
}

void DsnValidator::validateFieldFormats(void* xmlDoc, DsnValidationResult& result) {
    pugi::xml_document* doc = static_cast<pugi::xml_document*>(xmlDoc);

    // Helper lambda to recursively validate all nodes
    std::function<void(pugi::xml_node)> validateNode = [&](pugi::xml_node node) {
        if (!node) return;

        std::string nodeName = node.name();

        // Check SIRET fields
        if (nodeName.find("S21_G00_06_001") != std::string::npos ||
            nodeName.find("S21_G00_11_001") != std::string::npos) {
            std::string value = node.text().as_string();
            if (!value.empty()) {
                DsnValidationError error;
                error.field = nodeName;
                error.path = nodeName;
                if (!validateSiret(value, error)) {
                    result.errors.push_back(error);
                }
            }
        }

        // Check NIR fields (S21_G00_30_001)
        if (nodeName == "S21_G00_30_001") {
            std::string value = node.text().as_string();
            if (!value.empty()) {
                DsnValidationError error;
                error.field = nodeName;
                error.path = nodeName;
                if (!validateNir(value, error)) {
                    result.errors.push_back(error);
                }
            }
        }

        // Check date fields (pattern: ends with date-related field numbers)
        if (nodeName.find("_006") != std::string::npos ||  // Often birth dates
            nodeName.find("_007") != std::string::npos) {   // Often other dates
            std::string value = node.text().as_string();
            if (!value.empty() && value.length() == 8) {
                DsnValidationError error;
                error.field = nodeName;
                error.path = nodeName;
                if (!validateDate(value, error)) {
                    result.errors.push_back(error);
                }
            }
        }

        // Recursively validate children
        for (pugi::xml_node child : node.children()) {
            validateNode(child);
        }
    };

    // Start validation from root
    validateNode(doc->document_element());
}

} // namespace ariane_xml
