import os
from compliance_api import create_app


# Create the application
application = create_app()

print(f"App Name-----: {os.getenv('app_name', 'Not Set')}")
print(f"App Secret-----: {os.getenv('secret_key=', 'Not Set')}")


if __name__ == "__main__":

    # Print environment variables right before running the app
    print("App Environment Variables:---------3-------------")
    for k, v in os.environ.items():
        print(f"{k}: {v}")

    # Run the application
    application.run(debug=True, host='0.0.0.0', port=3200)
    
