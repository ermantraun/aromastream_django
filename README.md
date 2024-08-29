# Aromastream Django

This project is a Django web application that uses PostgreSQL as a database, and uses uwsgi + nginx  This `README md` explains how to run the project using Docker 

## Contents

- [Pre-requirements](#pre-requirements-pre-requirements)
- [Create a project network in Docker](#Create-a-project-network-in-Docker)
- [Project Launch](#start-project)
- [Project Structure](#project-structure)
- [Important Settings](#important-settings)
- [URL Templates](#url-templates)
- [Notes](#notes)

## <a name=“pre-requirements”></a> Pre-requirements

Make sure you have the following tools installed:

- <a href=“https://docs.docker.com/get-docker/” target=“_blank”>Docker</a>

## <a name=“create-project-network-in-docker”></a>Create a project network in Docker



Create a project network in Docker:

<pre><code>docker network create aromastream</code></pre> 


<h2>Starting the PostgreSQL image</h2>
<h3>0  Clone the repository</h3>
<h3>1  Build the Docker image</h3> 
<p>If you have not yet built a Docker image, run the following command into the db_dockerfile directory and execute:</p>
<pre><code>docker build -t postgres  </code></pre> 

<h3>2  Create a volume to store the data</h3>
<p>Create a PostgreSQL data storage volume to save data between container restarts:</p>
<pre><code>docker volume create postgres_data</code></pre> 

<h3>3  Start the container</h3> 
<p>You can start a PostgreSQL container without using environment variables  This method uses the default PostgreSQL settings specified in the Dockerfile:</p>
<pre><code>docker run -d \
  --name psg \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data 
  --network aromastream
  postgres</code></pre>
<ul>
    <li><code>-d</code>: Runs the container in the background </li>
    <li><code>--name my_postgres_container</code>: Specifies the name of the container </li>
    <li><code>-p 5432:5432</code>: Forces port 5432 of the container to port 5432 of the host </li>
    <li><code>-v postgres_data:/var/lib/postgresql/data</code>: Connects persistent storage for PostgreSQL data </li>
</ul>

## <a name=“start-project”></a> Project Startup 
    

<ol> 
    <li><b>Create a Docker image and start the container:</b>
        <pre><code>docker build -t aromastream_django  
docker run -it --name django -p 80:80 --network aromastream aromastream aromastream_django bash</code></pre>
        This will start the container with your application  Port 80 will be used for Django web service via Nginx and uWSGI 
    </li>
    <li><b>Apply migrations</b> 
        <pre><code>python manage py migrate</code></pre>
    </li>
    <li><b>Start Nginx and uWSGI:</b>
        <p>In the container, run the following commands to start Nginx and uWSGI:</p>
        <pre><code>service nginx start</code></pre>
        <pre><code>uwsgi --ini configs/uwsgi ini</code></pre>
        <p>These commands will start Nginx as a web server and uWSGI to handle requests to your Django application </p>
    </li>
</ol>






## <a name=“project-structure”></a>Project Structure

<ul>
    <li><b>Dockerfile</b> - file with instructions for building the Docker image </li>
    <li><b>requirements txt</b> - list of Python dependencies for the project </li>
    <li><b>manage py</b> - command line utility for managing your Django project </li>
    <li><b>api/</b> - the main directory of your project containing the Django application 
</ul>

## <a name=“important-settings”></a> Important Settings

### Database

The project uses PostgreSQL as the database  Connection settings:

<ul>
    <li><b>ENGINE:</b> django db backends postgresql - driver for working with PostgreSQL </li>
    <li><b>NAME:</b> django - name of the database </li>
    <li><b>USER:</b> django - user name to connect to the database </li>
    <li><b>PASSWORD:</b> 8995 - user password to connect to the database </li>
    <li><b>HOST:</b> 127 0 0 1 - address of the database server </li>
    <li><b>PORT:</b> 5432 - the port of the database server </li>
</ul>

### Security

<ul>
    <li><b>DEBUG:</b> True - debug mode including detailed error messages (not recommended for production environments) </li>
    <li><b>ALLOWED_HOSTS:</b> ['*'] - list of allowed hosts to access the application </li>
</ul>

### Applications and middleware

<ul>
    <li><b>INSTALLED_APPS:</b> include Django's base applications and additional applications such as <code>drf_spectacular</code> for automatically generating API schemas, <code>rest_framework</code> for building APIs, and <code>drf_api_logger</code> for logging requests </li>
    <li><b>MIDDLEWARE:</b> include standard Django middleware and <code>APILoggerMiddleware</code> for API logging </li>
</ul>

### JWT Authentication 

Uses the <code>rest_framework_simplejwt</code> library for authentication:

<ul>
    <li><b>SLIDING_TOKEN_LIFETIME:</b> 30 days is the lifetime of the JWT token </li>
    <li><b>SLIDING_TOKEN_REFRESH_LIFETIME:</b> 1 second - lifetime of the update token </li>
</ul>

### API Logging

<ul>
    <li><b>DRF_API_LOGGER_DATABASE:</b> True - enable logging of requests to the database </li>
    <li><b>DRF_LOGGER_QUEUE_MAX_SIZE:</b> 50 - maximum queue size for logging </li>
    <li><b>DRF_API_LOGGER_EXCLUDE_KEYS:</b> ['password', 'token'] - keys that will be excluded from the logs </li>
</ul>

### Configuring CORS

<ul>
    <li><b>CORS_ALLOWED_ORIGINS:</b> Not used - List of sources that are allowed to make cross-site HTTP requests</li>
    <li><b>CORS_ALLOW_ALL_ORIGINS:</b> True - If True, all sources will be allowed </li>
</ul>


### Advanced Settings

<ul>
    <li><b>ARDUINO_URL:</b> 'localhost:1203/{}' - URL to communicate with Arduino </li>
    <li><b>PAGE_SIZE:</b> 15 - page size for API pagination </li>
    <li><b>TIME_ZONE:</b> 'Europe/Moscow' - time zone setting </li>
</ul>

## <a name=“url-templates”></a>URL-templates

Below are the available API routes and their destinations:

<ul>
    <li><b>/admin/:</b> the Django admin interface for managing the application </li>
    <li><b>/api/:</b> the main prefix for all API endpoints  All API routes will be accessible via this path </li>
    <li><b>/api/login/:</b> <code>TokenObtainSlidingView</code> - get JWT token for authentication </li>
    <li><b>/api/signup/:</b> <code>UserCreateView</code> - creating a new user </li>
    <li><b>/api/user/:</b> <code>UserGetView</code> - getting information about the current user </li>
    <li><b>/api/user/update/:</b> <code>UserUpdateView</code> - updating the current user's data </li>
    <li><b>/api/password_reset/:</b> <code>UserPasswordUpdateView</code> - reset user's password </li>
    <li><b>/api/password_reset/confirm/:</b> <code>UserPasswordUpdateConfirmView</code> - confirm password reset </li>
    <li><b>/api/timestamps/:</b> <code>TimeStampCreateView</code> - creating new timestamps </li>
    <li><b>/api/timestamps/&lt;int:video_id&gt;/:</b> <code>TimeStampListView</code> - get a list of timestamps for the specified video </li>
    <li><b>/api/videos/:</b> <code>VideoListView</code> - get a list of videos </li>
    <li><b>/api/videos/&lt;int:video_id&gt;/:</b> <code>VideoDetailView</code> - get detailed information about the video </li>
    <li><b>/api/videos/popular/:</b> <code>PopularVideoListView</code> - get a list of popular videos </li>
    <li><b>/api/videos/search/:</b> <code>SearchVideoListView</code> - search video by criteria </li>
    <li><b>/api/arduino/trigger:</b> <code>TriggerListView</code> - call a trigger to interact with Arduino </li>
    <li><b>/api/schema/swagger-ui/:</b> <code>SpectacularSwaggerView</code> - display the API schema in the Swagger UI </li>
    <li><b>/api/schema/redoc/:</b> <code>SpectacularRedocView</code> - display the API schema in ReDoc </li>
</ul>

## <a name=“notes”></a> Notes

<ul>
    <li>The PostgreSQL user and database are created automatically when the container is started </li> 
    <li>To access the database, use the following parameters:
        <ul>
            <li><b>Host:</b> <name of the container with the DB on the same docker network></li>
            <li><b>Port:</b> 5432</li>
            <li><b>Username:</b> django</li>
            <li><b>Password:</b> 8995</li>
            <li><b>Database name:</b> django</li>
        </ul>
    </li>
    <li>For security, it is important to change the secret key from SECRET_KEY in Django settings </li>
</ul>

If you have any questions or concerns, please create an issue in the <a href=“https://github.com/ermantraun/aromastream_django” target=“_blank”>project repository</a> 
