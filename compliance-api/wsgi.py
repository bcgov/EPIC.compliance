import os
from compliance_api import create_app

# Print environment variables before app creation
print("App Environment Variables----------1----------:")
for k, v in os.environ.items():
    print(f"{k}: {v}")

# Create the application
application = create_app()

# Print environment variables after app creation
print("App Environment Variables:-----------2--------")
for k, v in os.environ.items():
    print(f"{k}: {v}")

if __name__ == "__main__":

    # Print environment variables right before running the app
    print("App Environment Variables:---------3-------------")
    for k, v in os.environ.items():
        print(f"{k}: {v}")

    # Run the application
    application.run(debug=True, host='0.0.0.0', port=3200)
    
