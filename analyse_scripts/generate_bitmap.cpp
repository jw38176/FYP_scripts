#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <filesystem>
#include <cmath>
#include <sstream>
#include <algorithm>
#include <unordered_map>
#include <numeric> 

namespace fs = std::filesystem;

int main() {
    std::string results_folder = "/home/jw38176/gem5/jw38176/results/microbench_logs_new";

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

        std::cout << "Analysing " << result << std::endl;

        fs::path result_path = result;

        std::vector<fs::path> prefetcher_folders;
        for (const auto& entry : fs::directory_iterator(result_path)) {
            if (fs::is_directory(entry)) {
                prefetcher_folders.push_back(entry.path());
            }
        }

        std::vector<uint64_t> max_address_list;

        for (const auto& prefetcher_folder : prefetcher_folders) {
            if (!fs::exists(prefetcher_folder / "max_addr.txt")) {
                std::cout << "Skipped " << prefetcher_folder.filename() << " (No max_addr.txt)" << std::endl;
                continue;
            }

            std::ifstream max_address_file(prefetcher_folder / "max_addr.txt");
            if (!max_address_file.is_open()) {
                std::cerr << "Failed to open max_addr.txt for reading in folder: " << prefetcher_folder << std::endl;
                continue;
            }

            uint64_t max_address;
            max_address_file >> max_address;
            max_address_list.push_back(max_address);
            max_address_file.close();
        }

        if (max_address_list.empty()) {
            continue;
        }

        uint64_t max_address = *std::max_element(max_address_list.begin(), max_address_list.end());

        std::cout << "Max address: " << max_address << std::endl;

        // Get sqrt of max address and round up
        uint64_t matrix_size = static_cast<uint64_t>(std::ceil(std::sqrt(max_address)));

        max_address = matrix_size * matrix_size;

        // Create a list of length max_address with all zeros
        std::unordered_map<fs::path, std::vector<uint8_t>> issued_vector_dict;
        std::unordered_map<fs::path, std::vector<uint8_t>> hit_vector_dict;

        for (const auto& prefetcher_folder : prefetcher_folders) {
            std::vector<uint8_t> issued_bitmap(max_address, 0);
            std::vector<uint8_t> hit_bitmap(max_address, 0);

            // Read the text files if they exist
            if (!fs::exists(prefetcher_folder / "issued.txt")) {
                std::cout << "Skipped " << prefetcher_folder.filename() << " (No issued.txt)" << std::endl;
                continue;
            }

            std::ifstream issued_file(prefetcher_folder / "issued.txt");
            std::ifstream hit_file(prefetcher_folder / "hit.txt");

            if (!issued_file.is_open() || !hit_file.is_open()) {
                std::cerr << "Failed to open one or more text files in folder: " << prefetcher_folder << std::endl;
                continue;
            }

            uint64_t address;
            while (issued_file >> address) {
                if (address < max_address) {
                    // The address and the following 7 addresses are issued
                    for (uint64_t i = 0; i < 8; ++i) {
                        issued_bitmap[address + i] = 1;
                    }
                }
            }

            while (hit_file >> address) {
                hit_bitmap[address] = 1;
            }

            issued_file.close();
            hit_file.close();

            std::cout << "Analysed " << prefetcher_folder.filename() << std::endl;

            issued_vector_dict[prefetcher_folder] = issued_bitmap;
            hit_vector_dict[prefetcher_folder] = hit_bitmap;

            // Convert bitmap to matrix
            std::vector<std::vector<uint8_t>> issued_matrix;
            std::vector<std::vector<uint8_t>> hit_matrix;

            for (uint64_t i = 0; i < max_address; i += matrix_size) {
                issued_matrix.push_back(std::vector<uint8_t>(issued_bitmap.begin() + i, issued_bitmap.begin() + std::min(i + matrix_size, max_address)));
                hit_matrix.push_back(std::vector<uint8_t>(hit_bitmap.begin() + i, hit_bitmap.begin() + std::min(i + matrix_size, max_address)));
            }

            // Save matrix
            std::ofstream issued_matrix_file(prefetcher_folder / "issued_matrix.txt");
            std::ofstream hit_matrix_file(prefetcher_folder / "hit_matrix.txt");

            if (!issued_matrix_file.is_open() || !hit_matrix_file.is_open()) {
                std::cerr << "Failed to open matrix text files for writing in folder: " << prefetcher_folder << std::endl;
                continue;
            }

            for (const auto& row : issued_matrix) {
                for (const auto& cell : row) {
                    issued_matrix_file << static_cast<int>(cell) << " ";
                }
                issued_matrix_file << std::endl;
            }

            for (const auto& row : hit_matrix) {
                for (const auto& cell : row) {
                    hit_matrix_file << static_cast<int>(cell) << " ";
                }
                hit_matrix_file << std::endl;
            }

            issued_matrix_file.close();
            hit_matrix_file.close();
        }

        std::cout << "Analysed all prefetchers" << std::endl;

        for (size_t i = 0; i < prefetcher_folders.size(); ++i) {
            for (size_t j = i + 1; j < prefetcher_folders.size(); ++j) {

                if (!fs::exists(prefetcher_folders[i] / "issued.txt") || !fs::exists(prefetcher_folders[j] / "issued.txt")) {
                    std::cout << "Skipped " << prefetcher_folders[i].filename() << " and " << prefetcher_folders[j].filename() << " (No issued.txt)" << std::endl;
                    continue;
                }

                std::cout << "Analysing " << prefetcher_folders[i].filename() << " and " << prefetcher_folders[j].filename() << std::endl;

                const auto& prefetcher_folder1 = prefetcher_folders[i];
                const auto& prefetcher_folder2 = prefetcher_folders[j];

                const auto& issued_bitmap1 = issued_vector_dict[prefetcher_folder1];
                const auto& issued_bitmap2 = issued_vector_dict[prefetcher_folder2];

                const auto& hit_bitmap1 = hit_vector_dict[prefetcher_folder1];
                const auto& hit_bitmap2 = hit_vector_dict[prefetcher_folder2];

                std::vector<uint8_t> issued_bitmap(max_address, 0);
                std::vector<uint8_t> hit_bitmap(max_address, 0);

                for (uint64_t k = 0; k < max_address; ++k) {
                    issued_bitmap[k] = issued_bitmap1[k] & issued_bitmap2[k];
                    hit_bitmap[k] = hit_bitmap1[k] & hit_bitmap2[k];
                }

                std::vector<std::vector<uint8_t>> issued_matrix;
                std::vector<std::vector<uint8_t>> hit_matrix;

                for (uint64_t i = 0; i < max_address; i += matrix_size) {
                    issued_matrix.push_back(std::vector<uint8_t>(issued_bitmap.begin() + i, issued_bitmap.begin() + std::min(i + matrix_size, max_address)));
                    hit_matrix.push_back(std::vector<uint8_t>(hit_bitmap.begin() + i, hit_bitmap.begin() + std::min(i + matrix_size, max_address)));
                }

                std::ofstream issued_matrix_file(result_path / (prefetcher_folder1.filename().string() + "_" + prefetcher_folder2.filename().string() + "_issued_matrix.txt"));
                std::ofstream hit_matrix_file(result_path / (prefetcher_folder1.filename().string() + "_" + prefetcher_folder2.filename().string() + "_hit_matrix.txt"));

                if (!issued_matrix_file.is_open() || !hit_matrix_file.is_open()) {
                    std::cerr << "Failed to open matrix text files for writing in folders: " << prefetcher_folder1 << " and " << prefetcher_folder2 << std::endl;
                    continue;
                }

                for (const auto& row : issued_matrix) {
                    for (const auto& cell : row) {
                        issued_matrix_file << static_cast<int>(cell) << " ";
                    }
                    issued_matrix_file << std::endl;
                }

                for (const auto& row : hit_matrix) {
                    for (const auto& cell : row) {
                        hit_matrix_file << static_cast<int>(cell) << " ";
                    }
                    hit_matrix_file << std::endl;
                }

                issued_matrix_file.close();
                hit_matrix_file.close();

                // Get the percentage of the intersection
                uint64_t issued_count = std::accumulate(issued_bitmap.begin(), issued_bitmap.end(), 0);
                uint64_t hit_count = std::accumulate(hit_bitmap.begin(), hit_bitmap.end(), 0);

                // Get the sum of the issued and hit bitmaps
                uint64_t sum_issued1 = std::accumulate(issued_bitmap1.begin(), issued_bitmap1.end(), 0);
                uint64_t sum_issued2 = std::accumulate(issued_bitmap2.begin(), issued_bitmap2.end(), 0);
                uint64_t sum_hit1 = std::accumulate(hit_bitmap1.begin(), hit_bitmap1.end(), 0);
                uint64_t sum_hit2 = std::accumulate(hit_bitmap2.begin(), hit_bitmap2.end(), 0);

                std::ofstream issued_percentage_file2(result_path / (prefetcher_folder2.filename().string() + "_" + prefetcher_folder1.filename().string() + "_issued_percentage.txt"));
                std::ofstream hit_percentage_file2(result_path / (prefetcher_folder2.filename().string() + "_" + prefetcher_folder1.filename().string() + "_hit_percentage.txt"));

                if (!issued_percentage_file2.is_open() || !hit_percentage_file2.is_open()) {
                    std::cerr << "Failed to open percentage text files for writing in folders: " << prefetcher_folder2 << " and " << prefetcher_folder1 << std::endl;
                    continue;
                }

                issued_percentage_file2 << (static_cast<double>(issued_count) / sum_issued2);
                hit_percentage_file2 << (static_cast<double>(hit_count) / sum_hit2);

                issued_percentage_file2.close();
                hit_percentage_file2.close();

                std::cout << "Analysed " << prefetcher_folder1.filename().string() << " and " << prefetcher_folder2.filename().string() << std::endl;
            }
        }

        std::cout << "Analysed all combinations" << std::endl;

        // Get the intersection of all prefetchers
        std::vector<uint8_t> issued_bitmap(max_address, 1);
        std::vector<uint8_t> hit_bitmap(max_address, 1);

        for (const auto& prefetcher_folder : prefetcher_folders) 
        {
            const auto& issued_bitmap1 = issued_vector_dict[prefetcher_folder];
            const auto& hit_bitmap1 = hit_vector_dict[prefetcher_folder];

            if (!fs::exists(prefetcher_folder / "issued.txt")) {
                std::cout << "Skipped " << prefetcher_folder.filename() << " (No issued.txt)" << std::endl;
                continue;
            }

            for (uint64_t k = 0; k < max_address; ++k) {
                issued_bitmap[k] &= issued_bitmap1[k];
                hit_bitmap[k] &= hit_bitmap1[k];
            }
        }

        std::cout << "Analysed all prefetchers" << std::endl;

        std::vector<std::vector<uint8_t>> issued_matrix;
        std::vector<std::vector<uint8_t>> hit_matrix;

        for (uint64_t i = 0; i < max_address; i += matrix_size) {
            issued_matrix.push_back(std::vector<uint8_t>(issued_bitmap.begin() + i, issued_bitmap.begin() + std::min(i + matrix_size, max_address)));
            hit_matrix.push_back(std::vector<uint8_t>(hit_bitmap.begin() + i, hit_bitmap.begin() + std::min(i + matrix_size, max_address)));
        }

        std::ofstream issued_matrix_file(result_path / "all_issued_matrix.txt");
        std::ofstream hit_matrix_file(result_path / "all_hit_matrix.txt");

        if (!issued_matrix_file.is_open() || !hit_matrix_file.is_open()) {
            std::cerr << "Failed to open matrix text files for writing in folder: " << result_path << std::endl;
            continue;
        }

        for (const auto& row : issued_matrix) {
            for (const auto& cell : row) {
                issued_matrix_file << static_cast<int>(cell) << " ";
            }
            issued_matrix_file << std::endl;
        }

        for (const auto& row : hit_matrix) {
            for (const auto& cell : row) {
                hit_matrix_file << static_cast<int>(cell) << " ";
            }
            hit_matrix_file << std::endl;
        }

        issued_matrix_file.close();
        hit_matrix_file.close();

        // Add all issued and hit bitmaps of all prefetchers
        std::vector<uint8_t> sum_issued_bitmap(max_address, 0);
        std::vector<uint8_t> sum_hit_bitmap(max_address, 0);

        for (const auto& prefetcher_folder : prefetcher_folders) {
            const auto& issued_bitmap1 = issued_vector_dict[prefetcher_folder];
            const auto& sum_hit_bitmap1 = hit_vector_dict[prefetcher_folder];

            if (!fs::exists(prefetcher_folder / "issued.txt")) {
                std::cout << "Skipped " << prefetcher_folder.filename() << " (No issued.txt)" << std::endl;
                continue;
            }

            for (uint64_t k = 0; k < max_address; ++k) {
                sum_issued_bitmap[k] += issued_bitmap1[k];
                sum_hit_bitmap[k] += sum_hit_bitmap1[k];
            }
        }

        std::vector<std::vector<uint8_t>> sum_issued_matrix;
        std::vector<std::vector<uint8_t>> sum_hit_matrix;

        for (uint64_t i = 0; i < max_address; i += matrix_size) {
            sum_issued_matrix.push_back(std::vector<uint8_t>(sum_issued_bitmap.begin() + i, sum_issued_bitmap.begin() + std::min(i + matrix_size, max_address)));
            sum_hit_matrix.push_back(std::vector<uint8_t>(sum_hit_bitmap.begin() + i, sum_hit_bitmap.begin() + std::min(i + matrix_size, max_address)));
        }

        std::ofstream sum_issued_matrix_file(result_path / "sum_issued_matrix.txt");
        std::ofstream sum_hit_matrix_file(result_path / "sum_hit_matrix.txt");

        if (!sum_issued_matrix_file.is_open() || !sum_hit_matrix_file.is_open()) {
            std::cerr << "Failed to open matrix text files for writing in folder: " << result_path << std::endl;
            continue;
        }

        for (const auto& row : sum_issued_matrix) {
            for (const auto& cell : row) {
                sum_issued_matrix_file << static_cast<int>(cell) << " ";
            }
            sum_issued_matrix_file << std::endl;
        }

        for (const auto& row : sum_hit_matrix) {
            for (const auto& cell : row) {
                sum_hit_matrix_file << static_cast<int>(cell) << " ";
            }
            sum_hit_matrix_file << std::endl;
        }

        sum_issued_matrix_file.close();
        sum_hit_matrix_file.close();

        
    }

    return 0;
}
