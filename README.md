# Distributed Scraping

Welcome to the Distributed Scrapy Project! This project is designed to demonstrate a highly scalable, distributed web scraping solution using Scrapy, a powerful Python library for extracting the data from websites. Our solution leverages Docker for containerization, PostgreSQL for task queue management, and AWS ECS for container orchestration.

# Overview

At Stackadoc, we specialize in implementing machine learning solutions across various domains. The accuracy of our predictions heavily relies on the quality and quantity of data, which we extract from the internet using Scrapy spiders. As our data gathering needs grew, we faced limitations with the single-machine, vertical scaling approach. To overcome this, we adopted a distributed architecture to horizontally scale our scraping tasks, significantly reducing data collection timeframes and enhancing system robustness.

## Key Components

Python Application: Core business logic written in Python, emphasizing clean code and modularity.

Poetry: Dependency management and packaging made easy with Poetry, ensuring consistent environments and straightforward dependency resolution.

Docker: Containerization support with Docker, facilitating development, testing, and deployment across different environments without any surprises.

Terraform: Infrastructure as Code (IaC) to provision and manage any cloud, infrastructure, or service.

SQLAlchemy: Database access and manipulation using SQLAlchemy, providing a high-level ORM and direct SQL access for efficient data handling.

PostgreSQL: Utilizing PostgreSQL as the relational database system of choice, known for its reliability, feature robustness, and performance.

# Getting Started
## Prerequisites

    Docker
    Python 3.10 or newer
    Poetry
    Terraform
    Access to a PostgreSQL server (either locally or a hosted instance)

## Setup

1. Clone the repository

```shell script

git clone https://github.com/yourusername/ProjectName.git
cd ProjectName

```

2. Install Dependencies with Poetry:

```shell script

poetry install

```

3. Environment Variables

Duplicate .env.example to .env and fill it with your PostgreSQL credentials and any other environment variables needed.

4. Running Locally

Using Docker Compose, you can spin up the application and the required databases for local development:

```shell script

docker-compose up --build

```


5. Database Migration

To create or migrate your database schema, run:

```shell script

poetry run alembic upgrade head

```


6. Deploy with Terraform

To provision your infrastructure on the cloud, navigate to the infrastructure directory:

```shell script

cd terraform

```

Initialize Terraform:

```shell script

terraform init

```

Apply configuration (Note: You might need to configure your cloud provider credentials):

```shell script

terraform apply

```

# Contributing

Your contributions are welcome! Whether it's improving the code, fixing bugs, or enhancing documentation, we value your help. Please feel free to fork the repository, make your changes, and submit a pull request.

# License

ProjectName is released under the GNU License.


# Acknowledgments

This work is a result of collaborative efforts from the Stackadoc team, aimed at pushing the boundaries of data collection for machine learning. We hope that sharing our journey and solution will benefit others facing similar scaling challenges.

Happy Scraping!