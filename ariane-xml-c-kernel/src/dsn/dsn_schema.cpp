#include "dsn/dsn_schema.h"
#include <algorithm>
#include <regex>

namespace ariane_xml {

DsnSchema::DsnSchema(const std::string& version)
    : version_(version) {}

void DsnSchema::addAttribute(const DsnAttribute& attr) {
    // Add to full name map
    full_name_map_[attr.full_name] = attr;

    // Add to shortcut map
    shortcut_map_[attr.short_id].push_back(attr);
}

void DsnSchema::addBloc(const DsnBloc& bloc) {
    bloc_index_[bloc.name] = blocs_.size();
    blocs_.push_back(bloc);
}

std::vector<DsnAttribute> DsnSchema::findByShortId(const std::string& short_id) const {
    auto it = shortcut_map_.find(short_id);
    if (it != shortcut_map_.end()) {
        return it->second;
    }
    return {};
}

DsnAttribute* DsnSchema::findByFullName(const std::string& full_name) {
    auto it = full_name_map_.find(full_name);
    if (it != full_name_map_.end()) {
        return &(it->second);
    }
    return nullptr;
}

const DsnAttribute* DsnSchema::findByFullName(const std::string& full_name) const {
    auto it = full_name_map_.find(full_name);
    if (it != full_name_map_.end()) {
        return &(it->second);
    }
    return nullptr;
}

const DsnBloc* DsnSchema::findBloc(const std::string& bloc_name) const {
    auto it = bloc_index_.find(bloc_name);
    if (it != bloc_index_.end()) {
        return &blocs_[it->second];
    }
    return nullptr;
}

std::vector<const DsnBloc*> DsnSchema::findBlocsByPattern(const std::string& pattern) const {
    std::vector<const DsnBloc*> results;
    std::regex regex_pattern(pattern, std::regex::icase);

    for (const auto& bloc : blocs_) {
        if (std::regex_search(bloc.name, regex_pattern) ||
            std::regex_search(bloc.label, regex_pattern)) {
            results.push_back(&bloc);
        }
    }

    return results;
}

bool DsnSchema::isAmbiguous(const std::string& short_id) const {
    auto it = shortcut_map_.find(short_id);
    if (it != shortcut_map_.end()) {
        return it->second.size() > 1;
    }
    return false;
}

} // namespace ariane_xml
