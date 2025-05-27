pipeline {
    agent {
        label 'agent-node2'
    }

    environment {
        APP_REPO = 'https://github.com/sandyxd18/flask-todolist.git'
        MANIFEST_REPO = 'https://github.com/sandyxd18/manifest-tubes.git'
        DOCKER_IMAGE = 'sandyxd18/backend-tubes'
        IMAGE_TAG = ''
        GIT_CREDENTIALS_ID = 'github-creds'
        DOCKER_CREDENTIALS_ID = 'a77b13b7-6e11-4652-9760-e73ef64c6d32'
        ARGOCD_CREDENTIALS_ID = 'argocd-creds'
        ARGOCD_SERVER = '192.168.22.172:31014'
        APP_NAME = 'backend'
    }

    stages {
        stage('Clone Backend Repo') {
            steps {
                git branch: 'main', url: "${APP_REPO}"
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    def imageTag = "v${env.BUILD_NUMBER}"
                    env.IMAGE_TAG = imageTag
                    // env.IMAGE_TAG = "v${env.BUILD_NUMBER}"
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker build -t ${DOCKER_IMAGE}:${imageTag} .
                            docker push ${DOCKER_IMAGE}:${imageTag}
                        """
                    }
                }
            }
        }

        stage('Clone Manifest Repo') {
            steps {
                dir('manifest') {
                    git url: "${MANIFEST_REPO}", branch: 'main'
                }
            }
        }

        stage('Update Image Tag') {
            steps {
                dir('manifest/backend-manifest') {
                    script {
                        def imageTag = "v${env.BUILD_NUMBER}"
                        env.IMAGE_TAG = imageTag
                        withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS_ID}", usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                            sh """
                                sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${imageTag}|' backend-deployment.yaml
                                git config user.name "jenkins"
                                git config user.email "jenkins@example.com"
                                git add .
                                git commit -m "Update image tag to ${imageTag}" || echo 'No changes to commit'

                                # Push dengan kredensial aman via HTTPS
                                git push https://$GIT_USER:$GIT_TOKEN@github.com/sandyxd18/manifest-tubes.git main
                            """
                        }
                    }
                }
            }
        }

        stage('Sync ArgoCD') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: ARGOCD_CREDENTIALS_ID, usernameVariable: 'ARGOCD_USER', passwordVariable: 'ARGOCD_PASS')]) {
                        sh """
                            argocd login ${ARGOCD_SERVER} --username $ARGOCD_USER --password $ARGOCD_PASS --insecure
                            argocd app sync ${APP_NAME} --prune
                        """
                    }
                }
            }
        }
    }
    post {
        // Clean after build
        always {
            cleanWs()
        }
    }
}