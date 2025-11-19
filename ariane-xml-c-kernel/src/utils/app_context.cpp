#include "utils/app_context.h"

namespace ariane_xml {

void AppContext::setXsdPath(const std::string& path) {
    xsd_path_ = path;
}

std::optional<std::string> AppContext::getXsdPath() const {
    return xsd_path_;
}

bool AppContext::hasXsdPath() const {
    return xsd_path_.has_value();
}

void AppContext::setDestPath(const std::string& path) {
    dest_path_ = path;
}

std::optional<std::string> AppContext::getDestPath() const {
    return dest_path_;
}

bool AppContext::hasDestPath() const {
    return dest_path_.has_value();
}

void AppContext::setVerbose(bool verbose) {
    verbose_ = verbose;
}

bool AppContext::isVerbose() const {
    return verbose_;
}

void AppContext::setMode(QueryMode mode) {
    mode_ = mode;
}

QueryMode AppContext::getMode() const {
    return mode_;
}

bool AppContext::isDsnMode() const {
    return mode_ == QueryMode::DSN;
}

void AppContext::setDsnVersion(const std::string& version) {
    dsn_version_ = version;
}

std::string AppContext::getDsnVersion() const {
    return dsn_version_;
}

void AppContext::setDsnSchema(std::shared_ptr<DsnSchema> schema) {
    dsn_schema_ = schema;
}

std::shared_ptr<DsnSchema> AppContext::getDsnSchema() const {
    return dsn_schema_;
}

bool AppContext::hasDsnSchema() const {
    return dsn_schema_ != nullptr;
}

void AppContext::setPseudoConfigPath(const std::string& path) {
    pseudo_config_path_ = path;
}

std::optional<std::string> AppContext::getPseudoConfigPath() const {
    return pseudo_config_path_;
}

bool AppContext::hasPseudoConfigPath() const {
    return pseudo_config_path_.has_value();
}

} // namespace ariane_xml
