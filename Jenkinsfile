#!groovy
def PROJECT_NAME = "parkeerrechten"
def SLACK_CHANNEL = '#opdrachten-deployments'
def PLAYBOOK = 'deploy.yml'
def SLACK_MESSAGE = [
    "title_link": BUILD_URL,
    "fields": [
        ["title": "Project","value": PROJECT_NAME],
        ["title": "Branch", "value": BRANCH_NAME, "short":true],
        ["title": "Build number", "value": BUILD_NUMBER, "short":true]
    ]
]



pipeline {
    agent any

    environment {
        SHORT_UUID = sh( script: "head /dev/urandom | tr -dc A-Za-z0-9 | head -c10", returnStdout: true).trim()
        COMPOSE_PROJECT_NAME = "${PROJECT_NAME}-${env.SHORT_UUID}"
        VERSION = env.BRANCH_NAME.replace('/', '-').toLowerCase().replace(
            'master', 'latest'
        )
        IS_RELEASE = "${env.BRANCH_NAME ==~ "release/.*"}"
    }

    stages {
        stage('Test') {
            steps {
                sh 'make lint'
                sh 'make test'
            }
        }

        stage('Build') {
            steps {
                sh 'make build'
            }
        }

        stage('Push and deploy') {
            when { 
                anyOf {
                    branch 'master'
                    buildingTag()
                    environment name: 'IS_RELEASE', value: 'true'
                }
            }
            stages {
                stage('Push semver') {
                    steps {
                        slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE << 
                            [
                                "color": "#D4DADF",
                                "title": "Starting deployment",
                            ]
                        ])
                        retry(3) {
                            sh 'make push_semver'
                        }
                    }
                }

                stage('Push acceptance') {
                    when { 
                        anyOf {
                            environment name: 'IS_RELEASE', value: 'true' 
                            branch 'master'
                        }
                    }
                    steps {
                        retry(3) {
                            sh 'VERSION=acceptance make push'
                        }

                        slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE << 
                            [
                                "color": "#36a64f",
                                "title": "Push acceptance image succeeded :rocket:",
                            ]
                        ])
                    }
                }

                stage('Push production') {
                    when { tag pattern: "v\\d+\\.\\d+\\.\\d+\\.*", comparator: "REGEXP" }
                    steps {
                        retry(3) {
                            sh 'VERSION=production make push'
                        }

                        slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE <<
                            [
                                "color": "#36a64f",
                                "title": "Push production image succeeded :rocket:",
                            ]
                        ])
                    }
                }
            }
        }

    }
    post {
        always {
            sh 'make clean'
        }
        failure {
            slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE << 
                [
                    "color": "#D53030",
                    "title": "Build failed :fire:",
                ]
            ])
        }
    }
}


