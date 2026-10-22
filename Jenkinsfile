
pipeline {
    agent any

    environment {
        // CI MySQL container details
        DB_HOST = 'money-management-ci-mysql-1'
        DB_PORT = '3306'
        DB_NAME = 'money_management'

        // Retrieve database credentials securely from Jenkins
        DB_CREDENTIALS = credentials('ci-mysql-credentials')
    }

    stages {

        stage('Create Virtual Environment') {
            steps {
                // Create an isolated Python environment for testing
                sh 'python3 -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                // Install application and test dependencies
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                // Run automated tests and generate coverage reports
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
                    // Locate the configured SonarQube Scanner
                    def scannerHome = tool 'SonarQube-Scanner'

                    // Inject SonarQube server configuration
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                // Stop the pipeline if the Quality Gate fails
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                // Create a uniquely tagged image for this Jenkins build
                sh 'docker build -t money-management:build-${BUILD_NUMBER} .'
            }
        }

        stage('Deploy, Verify, and Roll Back') {
            steps {
                // Deploy without bringing down MySQL.
                // If deployment or verification fails, restore the previous image.
                sh '''
                    set -eu

                    export APP_PORT="5001"
                    export DB_USER="$DB_CREDENTIALS_USR"
                    export DB_PASSWORD="$DB_CREDENTIALS_PSW"
                    export DB_NAME="money_management"

                    NEW_IMAGE="money-management:build-${BUILD_NUMBER}"

                    # Remember the currently deployed image before changing it.
                    PREVIOUS_IMAGE="$(docker inspect \
                        --format='{{.Config.Image}}' \
                        money-management-cd-app-1 2>/dev/null || true)"

                    echo "Previous image: ${PREVIOUS_IMAGE:-none}"
                    echo "New image: $NEW_IMAGE"

                    # Test the API from inside the deployed application container.
                    check_api() {
                        ATTEMPT=1
                        MAX_ATTEMPTS=6

                        while [ "$ATTEMPT" -le "$MAX_ATTEMPTS" ]; do
                            echo "API health check $ATTEMPT of $MAX_ATTEMPTS"

                            if docker exec money-management-cd-app-1 \
                                python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:5000/api/transactions', timeout=5); print('HTTP:', r.status); r.read()"; then
                                echo "API health check passed."
                                return 0
                            fi

                            if [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; then
                                sleep 5
                            fi

                            ATTEMPT=$((ATTEMPT + 1))
                        done

                        return 1
                    }

                    # Restore and verify the previous application image.
                    rollback_previous() {
                        if [ -z "$PREVIOUS_IMAGE" ]; then
                            echo "No previous image is available for rollback."
                            return 1
                        fi

                        echo "Rolling back to $PREVIOUS_IMAGE"

                        export APP_IMAGE="$PREVIOUS_IMAGE"

                        if ! docker compose -p money-management-cd \
                            up -d --no-deps app; then
                            echo "Rollback deployment command failed."
                            return 1
                        fi

                        if check_api; then
                            echo "Rollback successful. Previous API is healthy."
                            return 0
                        fi

                        echo "Rollback verification failed."
                        return 1
                    }

                    # Deploy the new version without stopping the database.
                    export APP_IMAGE="$NEW_IMAGE"

                    if ! docker compose -p money-management-cd \
                        up -d --no-deps app; then
                        echo "New deployment failed."

                        if rollback_previous; then
                            echo "Previous version restored."
                        else
                            echo "CRITICAL: Automatic rollback failed."
                        fi

                        exit 1
                    fi

                    # Verify the new release before marking deployment successful.
                    if check_api; then
                        echo "Deployment successful: $NEW_IMAGE"
                        exit 0
                    fi

                    echo "New deployment failed health verification."

                    if rollback_previous; then
                        echo "Previous version restored successfully."
                    else
                        echo "CRITICAL: Automatic rollback failed."
                    fi

                    # A rollback does not mean the new release succeeded.
                    exit 1
                '''
            }
        }
    }
}
