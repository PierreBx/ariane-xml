#ifndef COMMAND_HANDLER_H
#define COMMAND_HANDLER_H

#include "app_context.h"
#include <string>

namespace ariane_xml {

// Forward declarations
struct DsnAttribute;
struct DsnBloc;

class CommandHandler {
public:
    explicit CommandHandler(AppContext& context);

    // Returns true if the command was handled, false if it should be treated as a query
    bool handleCommand(const std::string& input);

private:
    AppContext& context_;

    bool handleSetCommand(const std::string& input);
    bool handleShowCommand(const std::string& input);
    bool handleGenerateCommand(const std::string& input);
    bool handleCheckCommand(const std::string& input);
    bool handleDescribeCommand(const std::string& input);
    bool handleDsnTemplateCommand(const std::string& input);
    bool handleDsnCompareCommand(const std::string& input);
    bool handlePseudonymiseCommand(const std::string& input);

    void setXsdPath(const std::string& path);
    void setDestPath(const std::string& path);
    void setPseudoConfigPath(const std::string& path);

    void showXsdPath();
    void showDestPath();
    void showMode();
    void showPseudoConfig();
    void showPseudonymisationStatus(const std::string& filepath);

    void displayAttribute(const DsnAttribute& attr);
    void displayBloc(const DsnBloc& bloc);

    bool validateXsdFile(const std::string& path);
    bool validateAndCreateDestDirectory(const std::string& path);
};

} // namespace ariane_xml

#endif // COMMAND_HANDLER_H
