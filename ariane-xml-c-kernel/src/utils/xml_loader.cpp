#include "utils/xml_loader.h"
#include "error/error_codes.h"
#include <algorithm>

namespace ariane_xml {

std::unique_ptr<pugi::xml_document> XmlLoader::load(const std::string& filepath) {
    auto doc = std::make_unique<pugi::xml_document>();

    pugi::xml_parse_result result = doc->load_file(filepath.c_str());

    if (!result) {
        // Check if it's a file not found error (status_file_not_found)
        if (result.status == pugi::status_file_not_found) {
            throw ARX_ERROR(ErrorCategory::FILE_OPERATIONS, ErrorCodes::FILE_NOT_FOUND,
                           "File not found: " + filepath);
        } else if (result.status == pugi::status_io_error) {
            throw ARX_ERROR(ErrorCategory::FILE_OPERATIONS, ErrorCodes::FILE_PERMISSION_DENIED,
                           "Cannot access file (permission denied or I/O error): " + filepath);
        } else {
            // Other XML parsing errors
            throw ARX_ERROR(ErrorCategory::FILE_OPERATIONS, ErrorCodes::FILE_XML_PARSE_ERROR,
                           "Failed to parse XML file: " + filepath + "\nError: " + result.description());
        }
    }

    return doc;
}

bool XmlLoader::isXmlFile(const std::string& filepath) {
    // Check file extension
    if (filepath.length() < 4) return false;

    std::string ext = filepath.substr(filepath.length() - 4);
    std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

    return ext == ".xml";
}

} // namespace ariane_xml
