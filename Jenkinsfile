pipeline {
	agent {
		docker { image 'ubuntu:20.04' }
	}
	
	stages {
		stage('Build') {
			steps {
				sh 'echo $PWD && ls -lh'
				sh 'echo "Hello World" > file'
				stash includes: './file', name: 'testfile'
            }
        }

		stage('Deploy') {
			steps {
				sh 'echo $PWD && ls -lh'
				unstash 'testfile'
				sh 'cat ./file'
			}
		}
    }
}