#include "dsn/dsn_templates.h"
#include <sstream>
#include <iomanip>
#include <algorithm>

namespace ariane_xml {

DsnTemplateManager::DsnTemplateManager() {
    initializeTemplates();
}

const DsnTemplate* DsnTemplateManager::getTemplate(const std::string& name) const {
    auto it = templates_.find(name);
    if (it != templates_.end()) {
        return &it->second;
    }
    return nullptr;
}

std::vector<DsnTemplate> DsnTemplateManager::listTemplates() const {
    std::vector<DsnTemplate> result;
    for (const auto& [name, tmpl] : templates_) {
        result.push_back(tmpl);
    }
    return result;
}

std::vector<DsnTemplate> DsnTemplateManager::listTemplatesByCategory(
    const std::string& category
) const {
    std::vector<DsnTemplate> result;
    for (const auto& [name, tmpl] : templates_) {
        if (tmpl.category == category) {
            result.push_back(tmpl);
        }
    }
    return result;
}

std::vector<std::string> DsnTemplateManager::getCategories() const {
    std::vector<std::string> categories;
    for (const auto& [name, tmpl] : templates_) {
        if (std::find(categories.begin(), categories.end(), tmpl.category) == categories.end()) {
            categories.push_back(tmpl.category);
        }
    }
    std::sort(categories.begin(), categories.end());
    return categories;
}

std::string DsnTemplateManager::expandTemplate(
    const std::string& name,
    const std::map<std::string, std::string>& params
) const {
    const DsnTemplate* tmpl = getTemplate(name);
    if (!tmpl) {
        return "";
    }

    return substituteParameters(tmpl->query, params);
}

std::string DsnTemplateManager::formatTemplateList(
    const std::vector<DsnTemplate>& templates
) {
    if (templates.empty()) {
        return "No templates available.\n";
    }

    std::ostringstream output;
    output << "\nAvailable DSN Templates:\n";
    output << "========================\n\n";

    std::string current_category;
    for (const auto& tmpl : templates) {
        if (tmpl.category != current_category) {
            current_category = tmpl.category;
            output << "\n[" << current_category << "]\n";
        }

        output << "  " << std::left << std::setw(25) << tmpl.name
               << " - " << tmpl.description << "\n";
    }

    output << "\nUsage: DSN_TEMPLATE <template_name>\n";
    output << "       DSN_TEMPLATE <template_name> SET param1=value1 ...\n";

    return output.str();
}

std::string DsnTemplateManager::formatTemplateDetails(const DsnTemplate& tmpl) {
    std::ostringstream output;
    output << "\nTemplate: " << tmpl.name << "\n";
    output << "Category: " << tmpl.category << "\n";
    output << "Description: " << tmpl.description << "\n";

    if (!tmpl.parameters.empty()) {
        output << "\nParameters:\n";
        for (const auto& param : tmpl.parameters) {
            output << "  - " << param << "\n";
        }
    }

    output << "\nQuery:\n";
    output << "------\n";
    output << tmpl.query << "\n";

    return output.str();
}

void DsnTemplateManager::addTemplate(const DsnTemplate& tmpl) {
    templates_[tmpl.name] = tmpl;
}

void DsnTemplateManager::initializeTemplates() {
    // Employee listing templates
    addTemplate(DsnTemplate(
        "list_employees",
        "List all employees with basic information",
        "SELECT S21_G00_30.S21_G00_30_002 AS nom, "
        "S21_G00_30.S21_G00_30_004 AS prenoms, "
        "S21_G00_30.S21_G00_30_006 AS date_naissance "
        "FROM ${file} "
        "WHERE S21_G00_30 IS NOT NULL",
        {"file"},
        "extraction"
    ));

    addTemplate(DsnTemplate(
        "list_employees_with_nir",
        "List all employees with their NIR",
        "SELECT S21_G00_30.S21_G00_30_001 AS nir, "
        "S21_G00_30.S21_G00_30_002 AS nom, "
        "S21_G00_30.S21_G00_30_004 AS prenoms "
        "FROM ${file} "
        "WHERE S21_G00_30.S21_G00_30_001 IS NOT NULL",
        {"file"},
        "extraction"
    ));

    // Contract templates
    addTemplate(DsnTemplate(
        "find_contracts",
        "Find employment contracts by type",
        "SELECT S21_G00_40.S21_G00_40_007 AS type_contrat, "
        "S21_G00_40.S21_G00_40_001 AS date_debut, "
        "S21_G00_40.S21_G00_40_002 AS date_fin "
        "FROM ${file} "
        "WHERE S21_G00_40.S21_G00_40_007 = '${contract_type}'",
        {"file", "contract_type"},
        "extraction"
    ));

    addTemplate(DsnTemplate(
        "list_cdi_contracts",
        "List all CDI (permanent) contracts",
        "SELECT S21_G00_40.S21_G00_40_007 AS type_contrat, "
        "S21_G00_40.S21_G00_40_001 AS date_debut "
        "FROM ${file} "
        "WHERE S21_G00_40.S21_G00_40_007 = 'CDI'",
        {"file"},
        "extraction"
    ));

    // Salary/payment templates
    addTemplate(DsnTemplate(
        "extract_salaries",
        "Extract salary information for all employees",
        "SELECT S21_G00_50.S21_G00_50_001 AS date_versement, "
        "S21_G00_50.S21_G00_50_002 AS montant, "
        "S21_G00_50.S21_G00_51.S21_G00_51_011 AS montant_remuneration "
        "FROM ${file} "
        "WHERE S21_G00_50 IS NOT NULL",
        {"file"},
        "extraction"
    ));

    addTemplate(DsnTemplate(
        "total_remunerations",
        "Calculate total remunerations",
        "SELECT COUNT(*) AS nombre_versements, "
        "SUM(S21_G00_51.S21_G00_51_011) AS total_remunerations "
        "FROM ${file} "
        "WHERE S21_G00_51.S21_G00_51_011 IS NOT NULL",
        {"file"},
        "analysis"
    ));

    // Validation templates
    addTemplate(DsnTemplate(
        "compliance_check_nir",
        "Check for employees without NIR",
        "SELECT S21_G00_30.S21_G00_30_002 AS nom, "
        "S21_G00_30.S21_G00_30_004 AS prenoms, "
        "S21_G00_30.S21_G00_30_001 AS nir "
        "FROM ${file} "
        "WHERE S21_G00_30 IS NOT NULL AND "
        "(S21_G00_30.S21_G00_30_001 IS NULL OR S21_G00_30.S21_G00_30_001 = '')",
        {"file"},
        "validation"
    ));

    addTemplate(DsnTemplate(
        "compliance_check_dates",
        "Check for invalid contract dates",
        "SELECT S21_G00_40.S21_G00_40_001 AS date_debut, "
        "S21_G00_40.S21_G00_40_002 AS date_fin "
        "FROM ${file} "
        "WHERE S21_G00_40 IS NOT NULL AND "
        "S21_G00_40.S21_G00_40_001 > S21_G00_40.S21_G00_40_002",
        {"file"},
        "validation"
    ));

    // Company/establishment templates
    addTemplate(DsnTemplate(
        "list_establishments",
        "List all establishments (SIRET)",
        "SELECT S21_G00_11.S21_G00_11_001 AS siret, "
        "S21_G00_11.S21_G00_11_016 AS nic "
        "FROM ${file} "
        "WHERE S21_G00_11 IS NOT NULL",
        {"file"},
        "extraction"
    ));

    addTemplate(DsnTemplate(
        "company_info",
        "Extract company information",
        "SELECT S21_G00_06.S21_G00_06_001 AS siren, "
        "S21_G00_06.S21_G00_06_002 AS raison_sociale, "
        "S21_G00_06.S21_G00_06_011 AS code_ape "
        "FROM ${file} "
        "WHERE S21_G00_06 IS NOT NULL",
        {"file"},
        "extraction"
    ));

    // Metadata templates
    addTemplate(DsnTemplate(
        "dsn_metadata",
        "Extract DSN file metadata",
        "SELECT S10_G00_00.S10_G00_00_001 AS logiciel, "
        "S10_G00_00.S10_G00_00_002 AS editeur, "
        "S10_G00_00.S10_G00_00_006 AS version_norme "
        "FROM ${file} "
        "WHERE S10_G00_00 IS NOT NULL",
        {"file"},
        "analysis"
    ));

    // Statistics templates
    addTemplate(DsnTemplate(
        "employee_statistics",
        "Count employees by various criteria",
        "SELECT COUNT(DISTINCT S21_G00_30.S21_G00_30_001) AS nombre_employes, "
        "COUNT(DISTINCT S21_G00_40) AS nombre_contrats "
        "FROM ${file}",
        {"file"},
        "analysis"
    ));

    addTemplate(DsnTemplate(
        "contract_type_distribution",
        "Distribution of contract types",
        "SELECT S21_G00_40.S21_G00_40_007 AS type_contrat, "
        "COUNT(*) AS nombre "
        "FROM ${file} "
        "WHERE S21_G00_40.S21_G00_40_007 IS NOT NULL "
        "GROUP BY S21_G00_40.S21_G00_40_007",
        {"file"},
        "analysis"
    ));

    // Search templates
    addTemplate(DsnTemplate(
        "find_employee_by_nir",
        "Find employee details by NIR",
        "SELECT S21_G00_30.S21_G00_30_001 AS nir, "
        "S21_G00_30.S21_G00_30_002 AS nom, "
        "S21_G00_30.S21_G00_30_004 AS prenoms, "
        "S21_G00_30.S21_G00_30_006 AS date_naissance "
        "FROM ${file} "
        "WHERE S21_G00_30.S21_G00_30_001 = '${nir}'",
        {"file", "nir"},
        "search"
    ));

    addTemplate(DsnTemplate(
        "find_employee_by_name",
        "Find employees by last name",
        "SELECT S21_G00_30.S21_G00_30_002 AS nom, "
        "S21_G00_30.S21_G00_30_004 AS prenoms, "
        "S21_G00_30.S21_G00_30_001 AS nir "
        "FROM ${file} "
        "WHERE S21_G00_30.S21_G00_30_002 LIKE '%${nom}%'",
        {"file", "nom"},
        "search"
    ));
}

std::string DsnTemplateManager::substituteParameters(
    const std::string& query,
    const std::map<std::string, std::string>& params
) const {
    std::string result = query;

    // Replace ${param} with actual values
    for (const auto& [key, value] : params) {
        std::string placeholder = "${" + key + "}";
        size_t pos = 0;
        while ((pos = result.find(placeholder, pos)) != std::string::npos) {
            result.replace(pos, placeholder.length(), value);
            pos += value.length();
        }
    }

    return result;
}

} // namespace ariane_xml
