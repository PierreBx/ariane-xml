#ifndef SECURE_INPUT_H
#define SECURE_INPUT_H

#include <string>

namespace ariane_xml {

/**
 * Utility class for secure input operations
 */
class SecureInput {
public:
    /**
     * Prompt for a password without echoing to terminal.
     *
     * @param prompt The prompt message to display
     * @return The entered password
     */
    static std::string promptPassword(const std::string& prompt = "Enter password: ");

    /**
     * Prompt for a password with confirmation.
     *
     * @param prompt The prompt message to display
     * @param confirmPrompt The confirmation prompt message
     * @return The entered password, or empty string if confirmation failed
     */
    static std::string promptPasswordWithConfirmation(
        const std::string& prompt = "Enter password: ",
        const std::string& confirmPrompt = "Confirm password: "
    );

    /**
     * Clear sensitive data from memory.
     *
     * @param data String to clear
     */
    static void secureClear(std::string& data);
};

} // namespace ariane_xml

#endif // SECURE_INPUT_H
