pipeline {
    agent any

    environment {
        // CI MySQL container hostname
        DB_HOST = 'money-management-ci-mysql-1'

        // MySQL internal Docker port
        DB_PORT = '3306'

        // CI database name
        DB_NAME = 'money_management'

        // Jenkins securely provides the database username and password
        DB_CREDENTIALS = credentials('ci-mysql-credentials')
    }

    stages {

        stage('Create Virtual Environment') {
            steps {
                // Create an isolated Python environment for this build
                sh 'python3 -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                // Install project dependencies inside the virtual environment
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                // Pass Jenkins credentials to the application through shell variables
                sh '''
                    export DB_USER="$DB_CREDENTIALS_USR"
                    export DB_PASSWORD="$DB_CREDENTIALS_PSW"

                    .venv/bin/python -m pytest \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    // Get the SonarQube Scanner configured in Jenkins
                    def scannerHome = tool 'SonarQube-Scanner'

                    // Load SonarQube server URL and authentication configuration
                    withSonarQubeEnv('SonarQube') {
                        // Run analysis using sonar-project.properties
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                // Wait for SonarQube to finish analysis and fail the pipeline
                // if the project does not meet the configured Quality Gate.
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                // Tag the Docker image with Jenkins BUILD_NUMBER.
                // This creates a unique image version for every CI build
                // and will later allow us to deploy or roll back a specific build.
                sh 'docker build -t money-management:build-${BUILD_NUMBER} .'
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                // Deploy the exact Docker image created by this Jenkins build.
                // Database credentials come from Jenkins credentials instead
                // of being stored in the repository.
                sh '''
                    export APP_IMAGE="money-management:build-${BUILD_NUMBER}"
                    export APP_PORT="5001"
                    export DB_USER="$DB_CREDENTIALS_USR"
                    export DB_PASSWORD="$DB_CREDENTIALS_PSW"
                    export DB_NAME="money_management"

                    docker compose -p money-management-cd down || true
                    docker compose -p money-management-cd up -d
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                // Retry the API check because the Flask application may need
                // some time to become ready after the container starts.
                sh '''
                    echo "Waiting for Flask application to become ready..."

                    MAX_ATTEMPTS=6
                    ATTEMPT=1

                    while [ "$ATTEMPT" -le "$MAX_ATTEMPTS" ]; do
                        echo "Health check attempt $ATTEMPT of $MAX_ATTEMPTS"

                        if curl --fail --silent --show-error \
                            http://localhost:5001/api/transactions; then

                            echo ""
                            echo "Application health check passed."
                            exit 0
                        fi

                        if [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; then
                            echo "Application is not ready yet. Waiting 5 seconds..."
                            sleep 5
                        fi

                        ATTEMPT=$((ATTEMPT + 1))
                    done

                    echo "Application health check failed."
                    echo "The deployed Flask API did not respond successfully."
                    exit 1
                '''
            }
        }
    }
}