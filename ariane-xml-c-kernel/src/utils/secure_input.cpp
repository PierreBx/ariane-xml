#include "utils/secure_input.h"
#include <iostream>
#include <termios.h>
#include <unistd.h>

namespace ariane_xml {

std::string SecureInput::promptPassword(const std::string& prompt) {
    // Display prompt
    std::cout << prompt;
    std::cout.flush();

    // Get current terminal settings
    struct termios oldSettings, newSettings;
    if (tcgetattr(STDIN_FILENO, &oldSettings) != 0) {
        // If we can't get terminal settings, fall back to normal input
        std::string password;
        std::getline(std::cin, password);
        return password;
    }

    // Disable echo
    newSettings = oldSettings;
    newSettings.c_lflag &= ~ECHO;

    if (tcsetattr(STDIN_FILENO, TCSANOW, &newSettings) != 0) {
        // If we can't set terminal settings, fall back to normal input
        std::string password;
        std::getline(std::cin, password);
        return password;
    }

    // Read password
    std::string password;
    std::getline(std::cin, password);

    // Restore terminal settings
    tcsetattr(STDIN_FILENO, TCSANOW, &oldSettings);

    // Print newline (since echo was disabled)
    std::cout << std::endl;

    return password;
}

std::string SecureInput::promptPasswordWithConfirmation(
    const std::string& prompt,
    const std::string& confirmPrompt
) {
    std::string password1 = promptPassword(prompt);
    std::string password2 = promptPassword(confirmPrompt);

    if (password1 != password2) {
        std::cerr << "Error: Passwords do not match\n";
        secureClear(password1);
        secureClear(password2);
        return "";
    }

    secureClear(password2);
    return password1;
}

void SecureInput::secureClear(std::string& data) {
    // Overwrite the string with zeros before clearing
    if (!data.empty()) {
        volatile char* p = &data[0];
        size_t size = data.size();
        while (size--) {
            *p++ = 0;
        }
        data.clear();
    }
}

} // namespace ariane_xml
