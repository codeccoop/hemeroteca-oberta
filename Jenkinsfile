pipeline {
	agent {
		docker { image 'node:16-alpine' }
	}
	
	stages {
		stage('Build') {
			steps {
				sh 'node --version > ./file'
				stash includes: './file', name: 'testfile'
            }
        }

		stage('Deploy') {
			steps {
				unstash 'testfile'
				sh 'echo $PWD && ls -lh'
				sh 'cat ./file'
			}
		}
    }
}