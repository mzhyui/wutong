import csv
import random
from typing import List

def generate_user_entries(n: int = 10, output_file: str = "user_activities.csv") -> None:
    """
    Generate random user activity entries.
    Args:
        n: Number of entries to generate
        output_file: Output CSV file name
    """
    # Define possible values
    arpu_levels = ['<50', '50-100', '>100']
    activities = [
        'gaming', 'streaming', 'music', 'video', 'shotvideo',
        'social', 'messaging', 'dating', 'news',
        'finance', 'productivity', 'learning', 'tool', 'utility',
        'take-away', 'shopping', 'travel', 'navigation', 'weather'
    ]
    roaming_types = ['local', 'remote']
    
    # Generate entries
    entries = []
    for i in range(1, n + 1):
        user_id = f"U{str(i).zfill(3)}"
        arpu_level = random.choice(arpu_levels)
        
        # Randomly select 2-5 activities
        num_activities = random.randint(2, 5)
        selected_activities = random.sample(activities, num_activities)
        app_preference = ';'.join(selected_activities)
        
        roaming_type = random.choice(roaming_types)
        
        entries.append([user_id, arpu_level, app_preference, roaming_type])
    
    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_id', 'arpu_level', 'app_preference', 'roaming_type'])
        writer.writerows(entries)
    
    print(f"Generated {n} entries in '{output_file}'")
    
    # Display sample
    print("\nSample of generated data:")
    for entry in entries[:5]:
        print(f"{entry[0]}, {entry[1]}, '{entry[2]}', {entry[3]}")

def analyze_data(filename: str = "user_activities.csv") -> None:
    """
    Analyze the generated data.
    """
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
        
        print(f"\nAnalysis of '{filename}':")
        print(f"Total entries: {len(data)}")
        
        # Count distributions
        arpu_counts = {}
        roaming_counts = {}
        
        for row in data:
            arpu = row['arpu_level']
            roaming = row['roaming_type']
            
            arpu_counts[arpu] = arpu_counts.get(arpu, 0) + 1
            roaming_counts[roaming] = roaming_counts.get(roaming, 0) + 1
        
        print("\nARPU Distribution:")
        for level, count in arpu_counts.items():
            percentage = (count / len(data)) * 100
            print(f"  {level}: {count} ({percentage:.1f}%)")
        
        print("\nRoaming Distribution:")
        for rtype, count in roaming_counts.items():
            percentage = (count / len(data)) * 100
            print(f"  {rtype}: {count} ({percentage:.1f}%)")
            
    except FileNotFoundError:
        print(f"File '{filename}' not found.")

if __name__ == "__main__":
    # Generate 20 entries
    generate_user_entries(n=50)
    
    # Analyze the data
    analyze_data("user_activities.csv")