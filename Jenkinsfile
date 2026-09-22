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
                    export DB_USER="$DB_CREDENTIALS_USR"
                    export DB_PASSWORD="$DB_CREDENTIALS_PSW"
                    export DB_NAME="money_management"

                    docker compose -p money-management-cd down || true
                    docker compose -p money-management-cd up -d
                '''
            }
        }
    }
}