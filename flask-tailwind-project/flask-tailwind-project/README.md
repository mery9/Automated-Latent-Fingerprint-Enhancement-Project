# Flask Tailwind Project

This project is a Flask web application that integrates Tailwind CSS for styling. Below are the instructions for setting up and using the project.

## Project Structure

```
flask-tailwind-project
├── static
│   ├── css
│   │   └── tailwind.css
│   ├── js
│   │   └── main.js
├── templates
│   ├── base.html
│   └── index.html
├── app.py
├── package.json
├── tailwind.config.js
└── README.md
```

## Steps to Integrate Tailwind CSS into Your Flask Project

1. **Install Tailwind CSS**:
   - Navigate to your project directory in the terminal.
   - Run `npm init -y` to create a `package.json` file if you haven't already.
   - Install Tailwind CSS and its dependencies by running:
     ```
     npm install tailwindcss postcss autoprefixer
     ```

2. **Create Tailwind Configuration**:
   - Run the following command to generate the `tailwind.config.js` file:
     ```
     npx tailwindcss init
     ```

3. **Configure Tailwind**:
   - In `tailwind.config.js`, set up the content paths to include your HTML files:
     ```javascript
     module.exports = {
       content: [
         './templates/**/*.html',
         './static/js/**/*.js',
       ],
       theme: {
         extend: {},
       },
       plugins: [],
     }
     ```

4. **Create a CSS File**:
   - In `static/css/tailwind.css`, add the following lines to import Tailwind's base, components, and utilities:
     ```css
     @tailwind base;
     @tailwind components;
     @tailwind utilities;
     ```

5. **Set Up PostCSS**:
   - Create a file named `postcss.config.js` in the root of your project and add the following:
     ```javascript
     module.exports = {
       plugins: {
         tailwindcss: {},
         autoprefixer: {},
       },
     }
     ```

6. **Build Tailwind CSS**:
   - Add a build script in your `package.json`:
     ```json
     "scripts": {
       "build:css": "postcss static/css/tailwind.css -o static/css/output.css"
     }
     ```
   - Run the build command:
     ```
     npm run build:css
     ```

7. **Link CSS in HTML**:
   - In `templates/base.html`, link the compiled CSS file:
     ```html
     <link href="{{ url_for('static', filename='css/output.css') }}" rel="stylesheet">
     ```

8. **Run Your Flask App**:
   - Start your Flask application by running:
     ```
     python app.py
     ```

9. **Development Workflow**:
   - Whenever you make changes to your Tailwind CSS, run the build command again to update `output.css`.

By following these steps, you will successfully integrate Tailwind CSS into your Flask project.