#ifndef PSEUDONYMISATION_CHECKER_H
#define PSEUDONYMISATION_CHECKER_H

#include <string>
#include <map>
#include <optional>

namespace ariane_xml {

// Marker constants (must match Python module)
const std::string PSEUDO_MARKER_TARGET = "ariane-pseudonymised";
const std::string PSEUDO_MARKER_VERSION = "1.0";

/**
 * Metadata from a pseudonymisation marker
 */
struct PseudonymisationMetadata {
    std::string version;      // Marker version
    std::string date;         // Pseudonymisation timestamp
    std::string tool;         // Tool used (ariane-xml-crypto)
    std::string config_hash;  // Hash of config used
};

/**
 * Utility class for checking pseudonymisation status of XML files
 */
class PseudonymisationChecker {
public:
    /**
     * Check if an XML file has been pseudonymised by ariane-xml.
     *
     * @param filepath Path to the XML file
     * @return true if the file contains the pseudonymisation marker
     */
    static bool isPseudonymised(const std::string& filepath);

    /**
     * Get pseudonymisation metadata from an XML file.
     *
     * @param filepath Path to the XML file
     * @return Metadata struct if found, std::nullopt otherwise
     */
    static std::optional<PseudonymisationMetadata> getMetadata(const std::string& filepath);

    /**
     * Format metadata as a human-readable string.
     *
     * @param metadata The metadata to format
     * @return Formatted string
     */
    static std::string formatMetadata(const PseudonymisationMetadata& metadata);
};

} // namespace ariane_xml

#endif // PSEUDONYMISATION_CHECKER_H
