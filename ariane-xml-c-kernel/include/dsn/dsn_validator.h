#ifndef DSN_VALIDATOR_H
#define DSN_VALIDATOR_H

#include "dsn_schema.h"
#include <string>
#include <vector>
#include <memory>

namespace ariane_xml {

/**
 * Validation result for DSN-specific checks
 */
struct DsnValidationError {
    std::string type;        // Error type (e.g., "SIRET_FORMAT", "NIR_CHECKSUM")
    std::string message;     // Human-readable error message
    std::string field;       // Field name (e.g., "S21_G00_30_001")
    std::string value;       // Invalid value
    std::string path;        // XML path to the element
};

struct DsnValidationResult {
    bool isValid = true;
    std::vector<DsnValidationError> errors;
    std::vector<std::string> warnings;
};

/**
 * DSN-specific validator
 * Performs additional validation beyond XSD schema validation
 */
class DsnValidator {
public:
    explicit DsnValidator(std::shared_ptr<DsnSchema> schema);

    /**
     * Validate a DSN XML file
     * @param xmlPath Path to the XML file
     * @return Validation result with DSN-specific errors and warnings
     */
    DsnValidationResult validate(const std::string& xmlPath);

private:
    std::shared_ptr<DsnSchema> schema_;

    /**
     * Validate SIRET format (9 digits + 5 digits)
     */
    bool validateSiret(const std::string& siret, DsnValidationError& error);

    /**
     * Validate NIR format (15 digits with checksum)
     */
    bool validateNir(const std::string& nir, DsnValidationError& error);

    /**
     * Validate date format (JJMMAAAA or AAAAMMJJ)
     */
    bool validateDate(const std::string& date, DsnValidationError& error);

    /**
     * Check if mandatory blocs are present
     */
    void checkMandatoryBlocs(void* xmlDoc, DsnValidationResult& result);

    /**
     * Check version coherence
     */
    void checkVersionCoherence(void* xmlDoc, DsnValidationResult& result);

    /**
     * Validate specific field formats
     */
    void validateFieldFormats(void* xmlDoc, DsnValidationResult& result);
};

} // namespace ariane_xml

#endif // DSN_VALIDATOR_H
