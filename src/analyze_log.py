import os

def analyze_log(file_path):
    total_volume = 0.0

    with open(file_path, 'r') as file:
        for line in file:
            if "qty:" in line:
                parts = line.split()
                qty = float(parts[parts.index("qty:") + 1].strip(','))
                buy_price = float(parts[parts.index("buyPrice:") + 1].strip(','))
                total_volume += qty * buy_price

    return total_volume

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python analyze_log.py <log_file_path>")
        sys.exit(1)
    log_file_path = sys.argv[1]
    if os.path.exists(log_file_path):
        total_volume = analyze_log(log_file_path)
        print(f"Total trading volume for the day: {total_volume}")
    else:
        print(f"Log file not found: {log_file_path}")
