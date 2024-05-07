# di-clutter
A project application about projects. works in Python 3.11 and 3.12 probably.


## Steps to install and run:
1. Clone repository
   ```bash
   git clone https://github.com/ellisgroenveld/di-clutter.git
   cd di-clutter
   ```
2. Create and activate environment
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
4. If you're on the main branch, do 
   ```bash
   export GH_TOKEN=YOUR_TOKEN
   ``` 
   where `YOUR_TOKEN` is the Github developer portal API token you have. Read more about that below. 
   
   If you're on the OrganisationTester branch, it's
   ```bash
   export GH_TOKEN2=YOUR_TOKEN
   ``` 
5. Run code
   ```bash
   python run.py
   ```


## GitHub API Key Explanation:

To run this project, you need to generate a personal access token from the GitHub Developer Portal. This token allows the application to interact with the GitHub API on your behalf, enabling features such as listing repositories and fetching repository information.

#### Steps to Generate a Personal Access Token:

1. **Navigate to GitHub Developer Settings:**
   - Go to your GitHub account settings and click on "Developer settings" from the sidebar menu.

2. **Create a New Personal Access Token:**
   - In the Developer settings menu, click on "Personal access tokens" and then click the "Generate new token" button.

3. **Configure Token Permissions:**
   - Give your token a descriptive name to remember its purpose.
   - Choose the appropriate scopes based on the functionalities your application requires. For this project, you'll need at least the `repo` scope to access repository information.

4. **Generate the Token:**
   - After selecting the desired scopes, click the "Generate token" button.
   - Copy the generated token to your clipboard. **Note**: Once you leave the page, you won't be able to see the token again.

5. **Set the Environment Variable:**
   - In your project directory, export the token as an environment variable using the command specified in the installation steps:
     ```bash
     export GH_TOKEN=YOUR_TOKEN
     ```
     Replace `YOUR_TOKEN` with the token you generated in step 4.

6. **Run the Application:**
   - With the environment variable set, you can now run the application using the provided command:
     ```bash
     python run.py
     ```

7. **Important Note:**
   - Treat your personal access token with care and keep it confidential. Do not expose it in public repositories or share it with others. If your token is compromised, revoke it immediately from the GitHub Developer Settings.
