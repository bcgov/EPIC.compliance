from compliance_api import create_app

print("App Environment Variables----------1----------:")
for k, v in os.environ.items():
    print(f"{k}: {v}")

application = create_app()


print("App Environment Variables:-----------2--------")
for k, v in os.environ.items():
    print(f"{k}: {v}")


if __name__ == "__main__":

    print("App Environment Variables:---------3-------------")
    for k, v in os.environ.items():
    print(f"{k}: {v}")

    
    application.run(debug=True, host='0.0.0.0', port=3200)
