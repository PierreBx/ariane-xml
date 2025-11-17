#ifndef DSN_TEMPLATES_H
#define DSN_TEMPLATES_H

#include <string>
#include <vector>
#include <map>
#include <memory>

namespace ariane_xml {

/**
 * Represents a predefined DSN query template
 */
struct DsnTemplate {
    std::string name;           // Template identifier (e.g., "list_employees")
    std::string description;    // Human-readable description
    std::string query;          // The SQL query template
    std::vector<std::string> parameters;  // Optional parameters for the template
    std::string category;       // Category (e.g., "extraction", "validation")

    DsnTemplate() = default;
    DsnTemplate(const std::string& n, const std::string& desc,
                const std::string& q, const std::vector<std::string>& params = {},
                const std::string& cat = "general")
        : name(n), description(desc), query(q), parameters(params), category(cat) {}
};

/**
 * Manages predefined DSN query templates
 * Provides common queries for:
 * - Listing employees (INDIVIDU)
 * - Finding contracts (CONTRAT)
 * - Extracting salaries (VERSEMENT)
 * - Compliance checks
 * - Data validation
 */
class DsnTemplateManager {
public:
    DsnTemplateManager();

    /**
     * Get a template by name
     * @param name Template identifier
     * @return Template if found, nullptr otherwise
     */
    const DsnTemplate* getTemplate(const std::string& name) const;

    /**
     * List all available templates
     * @return Vector of all templates
     */
    std::vector<DsnTemplate> listTemplates() const;

    /**
     * List templates by category
     * @param category Category name
     * @return Vector of templates in that category
     */
    std::vector<DsnTemplate> listTemplatesByCategory(const std::string& category) const;

    /**
     * Get all available categories
     * @return Vector of category names
     */
    std::vector<std::string> getCategories() const;

    /**
     * Execute a template with given parameters
     * @param name Template name
     * @param params Parameter values to substitute
     * @return The query with parameters substituted
     */
    std::string expandTemplate(const std::string& name,
                               const std::map<std::string, std::string>& params = {}) const;

    /**
     * Format template list for display
     * @param templates Templates to format
     * @return Formatted string for terminal output
     */
    static std::string formatTemplateList(const std::vector<DsnTemplate>& templates);

    /**
     * Format template details for display
     * @param tmpl Template to format
     * @return Formatted string showing template details
     */
    static std::string formatTemplateDetails(const DsnTemplate& tmpl);

private:
    std::map<std::string, DsnTemplate> templates_;

    /**
     * Initialize predefined templates
     */
    void initializeTemplates();

    /**
     * Add a template to the collection
     */
    void addTemplate(const DsnTemplate& tmpl);

    /**
     * Substitute parameters in a query template
     */
    std::string substituteParameters(const std::string& query,
                                     const std::map<std::string, std::string>& params) const;
};

} // namespace ariane_xml

#endif // DSN_TEMPLATES_H
