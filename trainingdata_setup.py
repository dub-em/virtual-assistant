import json
import variable

def training():
    data = variable.conv_or_comm_data

    training_data = data[:80]
    testing_data = data[80:]

    # File path to save the JSON file
    json_file_path_1 = "training_data.jsonl"
    json_file_path_2 = "testing_data.jsonl"

    # Write training data to JSON file
    # with open(json_file_path_1, "w") as json_file:
    #     json.dump(training_data, json_file, indent=4)

    # with open(json_file_path_2, "w") as json_file:
    #     json.dump(testing_data, json_file, indent=4)

    with open(json_file_path_1, "w") as jsonl_file:
        for example in training_data:
            json.dump(example, jsonl_file)
            jsonl_file.write('\n')

    with open(json_file_path_2, "w") as jsonl_file:
        for example in testing_data:
            json.dump(example, jsonl_file)
            jsonl_file.write('\n')

    print(f"Training data saved to {json_file_path_1}")
    print(f"Testing data saved to {json_file_path_2}")


if __name__ == "__main__":
    training()