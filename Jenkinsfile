pipeline {
    agent { label 'main-app' }

    stages {
        stage('Bump version') {
            steps {
                container('jnlp') {
                    withCredentials([usernamePassword(
                        credentialsId: 'github-credentials',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_TOKEN'
                    )]) {
                        sh '''
                            git config user.name "jenkins-bot"
                            git config user.email "tech@volopay.co"

                            VERSION=$(grep '^version' pyproject.toml | head -1 | sed 's/version = "\\(.*\\)"/\\1/')
                            MAJOR=$(echo $VERSION | cut -d. -f1)
                            MINOR=$(echo $VERSION | cut -d. -f2)
                            PATCH=$(echo $VERSION | cut -d. -f3)
                            NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"

                            sed -i "s/^version = \\"$VERSION\\"/version = \\"$NEW_VERSION\\"/" pyproject.toml

                            git add pyproject.toml
                            git commit -m "chore: bump version to v${NEW_VERSION}"
                            git tag "v${NEW_VERSION}"

                            git push https://${GIT_USER}:${GIT_TOKEN}@github.com/Volopay/vp-python-core.git master --tags
                        '''
                    }
                }
            }
        }
    }
}
