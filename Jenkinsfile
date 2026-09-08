pipeline {
    agent any

    stages {

        stage('Create Virtual Environment') {
            steps {
                sh 'python3 -m venv .venv'
            }
        }

        stage('Hello') {
            steps {
                echo 'Money Management CI Pipeline started'
            }
        }

    }
}