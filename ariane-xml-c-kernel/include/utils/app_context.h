#ifndef APP_CONTEXT_H
#define APP_CONTEXT_H

#include <string>
#include <optional>
#include <memory>

namespace ariane_xml {

// Forward declaration for DSN schema
class DsnSchema;

// Query mode enum
enum class QueryMode {
    STANDARD,
    DSN
};

// Stores application context/settings during a session
class AppContext {
public:
    AppContext() = default;

    // XSD file path management
    void setXsdPath(const std::string& path);
    std::optional<std::string> getXsdPath() const;
    bool hasXsdPath() const;

    // Destination directory management
    void setDestPath(const std::string& path);
    std::optional<std::string> getDestPath() const;
    bool hasDestPath() const;

    // Verbose mode management
    void setVerbose(bool verbose);
    bool isVerbose() const;

    // Query mode management (DSN vs STANDARD)
    void setMode(QueryMode mode);
    QueryMode getMode() const;
    bool isDsnMode() const;

    // DSN version management
    void setDsnVersion(const std::string& version);
    std::string getDsnVersion() const;

    // DSN schema management
    void setDsnSchema(std::shared_ptr<DsnSchema> schema);
    std::shared_ptr<DsnSchema> getDsnSchema() const;
    bool hasDsnSchema() const;

private:
    std::optional<std::string> xsd_path_;
    std::optional<std::string> dest_path_;
    bool verbose_ = false;

    // DSN mode fields
    QueryMode mode_ = QueryMode::STANDARD;
    std::string dsn_version_ = "AUTO";
    std::shared_ptr<DsnSchema> dsn_schema_;
};

} // namespace ariane_xml

#endif // APP_CONTEXT_H
