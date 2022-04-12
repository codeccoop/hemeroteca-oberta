pipeline {
	agent {
		docker { image 'node:16-alpine' }
	}
	
	stages {
		stage('Build') {
			steps {
				sh 'node --version > file'
				stash includes: './file', name: 'testfile'
            }
        }

		stage('Deploy') {
			steps {
				sh 'echo $PWD && ls -lh'
				{ unstash 'testfile' }
				sh 'cat ./file'
			}
		}
    }
}