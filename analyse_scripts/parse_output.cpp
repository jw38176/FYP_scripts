#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <filesystem>
#include <sstream>
#include <algorithm>

namespace fs = std::filesystem;

int main() {
    std::string results_folder = "/home/jw38176/gem5/jw38176/results/microbench_logs_new";
    std::regex log_pattern(R"(((\d+):\s*([A-Z]+)(0x[0-9a-f]+)))");

    // Get all folders in the results folder
    std::vector<fs::path> folders;

    for (const auto& entry : fs::directory_iterator(results_folder)) {
        if (fs::is_directory(entry)) {
            folders.push_back(entry.path());
        }
    }

    for (const auto& result : folders) {
         
        // skip .git
        if (result.filename() == ".git") {
            continue;
        }

        std::cout << "Parsing " << result << std::endl;

        fs::path result_path = result;

        std::vector<fs::path> prefetcher_folders;
        for (const auto& entry : fs::directory_iterator(result_path)) {
            if (fs::is_directory(entry)) {
                prefetcher_folders.push_back(entry.path());
            }
        }

        std::vector<uint64_t> issued_vector;
        std::vector<uint64_t> hit_vector;
        std::vector<uint64_t> unused_vector;

        std::vector<uint64_t> issued_tick_vector;
        std::vector<uint64_t> hit_tick_vector;
        std::vector<uint64_t> unused_tick_vector;

        for (const auto& prefetcher_folder : prefetcher_folders) {
            

            std::ifstream file(prefetcher_folder / "run.log");
            std::string line;

            while (std::getline(file, line)) {
                std::smatch match;
                try{
                    if (std::regex_search(line, match, log_pattern)) {
                        uint64_t tick = std::stoll(match[2].str());
                        std::string type = match[3].str();
                        uint64_t address = std::stoul(match[4].str(), nullptr, 16);

                        if (type == "PF") {
                            issued_vector.push_back(address);
                            issued_tick_vector.push_back(tick);
                        } else if (type == "HIT") {
                            hit_vector.push_back(address);
                            hit_tick_vector.push_back(tick);
                        } else if (type == "UPF") {
                            unused_vector.push_back(address);
                            unused_tick_vector.push_back(tick);
                        }
                    }
                } catch (std::invalid_argument& e) {
                    std::cout << "Invalid argument: " << e.what() << std::endl;
                    std::cout << "Line: " << line << std::endl;
                } catch (std::out_of_range& e) {
                    std::cout << "Out of range: " << e.what() << std::endl;
                    std::cout << "Line: " << line << std::endl;
                }

            }

            // If there are no issued or hit addresses, skip this prefetcher
            if (issued_vector.empty() || hit_vector.empty()) {
                std::cout << "Skipped " << prefetcher_folder.filename() << " (No issued or hit addresses)" << std::endl;
                continue;
            }

            // Find the largest address from the issued and hit vectors
            uint64_t max_address = std::max(*std::max_element(issued_vector.begin(), issued_vector.end()), 
                                            *std::max_element(hit_vector.begin(), hit_vector.end()));

            // Save max address to text file
            std::ofstream max_address_file(prefetcher_folder / "max_addr.txt");
            max_address_file << max_address;
            max_address_file.close();

            // Output to text files
            std::ofstream issued_file(prefetcher_folder / "issued.txt");
            std::ofstream hit_file(prefetcher_folder / "hit.txt");
            std::ofstream unused_file(prefetcher_folder / "unused.txt");

            std::ofstream issued_tick_file(prefetcher_folder / "issued_tick.txt");
            std::ofstream hit_tick_file(prefetcher_folder / "hit_tick.txt");
            std::ofstream unused_tick_file(prefetcher_folder / "unused_tick.txt");

            for (const auto& addr : issued_vector) {
                issued_file << addr << std::endl;
            }
            for (const auto& addr : hit_vector) {
                hit_file << addr << std::endl;
            }
            for (const auto& addr : unused_vector) {
                unused_file << addr << std::endl;
            }

            for (const auto& tick : issued_tick_vector) {
                issued_tick_file << tick << std::endl;
            }
            for (const auto& tick : hit_tick_vector) {
                hit_tick_file << tick << std::endl;
            }
            for (const auto& tick : unused_tick_vector) {
                unused_tick_file << tick << std::endl;
            }

            issued_file.close();
            hit_file.close();
            unused_file.close();

            issued_tick_file.close();
            hit_tick_file.close();
            unused_tick_file.close();
        }
    }

    return 0;
}
