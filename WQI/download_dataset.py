import kagglehub

# Download latest version of the dataset
path = kagglehub.dataset_download("akkshaysr/nwmp-water-quality-data-for-indian-lakes")

print("✅ Dataset downloaded successfully!")
print("📂 Path to dataset files:", path)
