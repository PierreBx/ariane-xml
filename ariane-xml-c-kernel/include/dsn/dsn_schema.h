#ifndef DSN_SCHEMA_H
#define DSN_SCHEMA_H

#include <string>
#include <vector>
#include <map>
#include <memory>

namespace ariane_xml {

/**
 * Represents a DSN attribute/field in the schema
 * Example: S21_G00_30_001 (NIR)
 */
struct DsnAttribute {
    std::string full_name;       // S21_G00_30_001
    std::string short_id;        // 30_001 (YY_ZZZ notation)
    std::string bloc_name;       // S21.G00.30 (INDIVIDU)
    std::string bloc_label;      // Human-readable bloc name (e.g., "INDIVIDU")
    std::string description;     // "NIR - Numéro d'inscription au répertoire"
    std::string type;            // "Alphanumeric 1-15"
    bool mandatory;              // Is this field mandatory?
    int min_occurs;              // Minimum occurrences (0 = optional)
    int max_occurs;              // Maximum occurrences (-1 = unbounded)
    std::vector<std::string> versions;  // ["P25V01", "P26V01"]

    DsnAttribute()
        : mandatory(false), min_occurs(0), max_occurs(1) {}
};

/**
 * Represents a DSN bloc/structure
 * Example: S21.G00.30 (INDIVIDU)
 */
struct DsnBloc {
    std::string name;            // S21.G00.30
    std::string label;           // INDIVIDU
    std::string description;     // Description of the bloc
    std::vector<DsnAttribute> attributes;  // All attributes in this bloc
    bool mandatory;              // Is this bloc mandatory?
    int min_occurs;              // Minimum occurrences
    int max_occurs;              // Maximum occurrences (-1 = unbounded)

    DsnBloc()
        : mandatory(false), min_occurs(0), max_occurs(1) {}
};

/**
 * Main DSN schema representation
 * Parsed from P25/P26 XSD files
 */
class DsnSchema {
public:
    DsnSchema() = default;
    explicit DsnSchema(const std::string& version);

    // Version information
    std::string getVersion() const { return version_; }
    void setVersion(const std::string& version) { version_ = version; }

    // Add attributes and blocs
    void addAttribute(const DsnAttribute& attr);
    void addBloc(const DsnBloc& bloc);

    // Lookup methods
    std::vector<DsnAttribute> findByShortId(const std::string& short_id) const;
    DsnAttribute* findByFullName(const std::string& full_name);
    const DsnAttribute* findByFullName(const std::string& full_name) const;

    // Bloc lookup
    const DsnBloc* findBloc(const std::string& bloc_name) const;
    std::vector<const DsnBloc*> findBlocsByPattern(const std::string& pattern) const;

    // Check for ambiguity
    bool isAmbiguous(const std::string& short_id) const;

    // Get all shortcuts mapped to full names
    const std::map<std::string, std::vector<DsnAttribute>>& getShortcutMap() const {
        return shortcut_map_;
    }

    // Get all blocs
    const std::vector<DsnBloc>& getBlocs() const {
        return blocs_;
    }

    // Get all attributes
    const std::map<std::string, DsnAttribute>& getAttributes() const {
        return full_name_map_;
    }

private:
    std::string version_;  // P25, P26, etc.

    // Shortcut notation mapping: "30_001" -> [DsnAttribute, ...]
    std::map<std::string, std::vector<DsnAttribute>> shortcut_map_;

    // Full name mapping: "S21_G00_30_001" -> DsnAttribute
    std::map<std::string, DsnAttribute> full_name_map_;

    // Bloc storage
    std::vector<DsnBloc> blocs_;
    std::map<std::string, size_t> bloc_index_;  // bloc name -> index in blocs_
};

} // namespace ariane_xml

#endif // DSN_SCHEMA_H
