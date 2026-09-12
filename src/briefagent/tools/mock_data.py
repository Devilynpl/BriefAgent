from typing import Dict, List, Optional

# Offline deterministic mock database for 25 benchmark companies & adversarial cases
BENCHMARK_MOCK_DATA: Dict[str, dict] = {
    "snowflake.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Route53 / Cloudflare"},
        "search": [
            {"title": "Snowflake - The Data Cloud Platform", "url": "https://snowflake.com", "snippet": "Snowflake Data Cloud allows enterprises to unite siloed data, discover and securely share data, and execute diverse analytic workloads using usage-based subscription pricing."},
            {"title": "Snowflake Headcount & Company Facts", "url": "https://snowflake.com/about", "snippet": "Founded in 2012, Snowflake employs over 7,000 employees globally with headquarters in Bozeman, Montana."},
            {"title": "Snowflake Cortex AI & Engineering Stack", "url": "https://snowflake.com/blog/cortex-ai", "snippet": "Snowflake expanded its stack with Cortex AI, Python Snowpark, LLM integration, and Iceberg tables in the past 12 months."},
            {"title": "Snowflake Sales & Expansion Triggers", "url": "https://snowflake.com/news/q4-expansion", "snippet": "Recent triggers include aggressive EMEA enterprise expansion, launching native apps on marketplace, and accelerating generative AI cloud migrations."},
        ],
        "scrape": {
            "https://snowflake.com": "# Snowflake Data Cloud\nSnowflake provides a single, integrated platform that offers that data warehouse, data lake, data engineering, data science, and modern data application development. Revenue model is based on consumption credits.",
            "https://snowflake.com/about": "# About Snowflake\nSnowflake powers over 9,000 customers worldwide with 7,200+ employees globally as of 2024. Headquartered in Bozeman, MT.",
            "https://snowflake.com/blog/cortex-ai": "# Snowflake Cortex AI Announcement\nIntroducing Snowflake Cortex for generative AI, supporting open source models like Llama 3, built using Python, C++, and Go on AWS/Azure/GCP infrastructure.",
            "https://snowflake.com/news/q4-expansion": "# Growth & Sales Triggers\nSnowflake is hiring over 500 sales engineers in EMEA and APAC, driving massive enterprise migrations from legacy on-premise databases.",
        }
    },
    "datadoghq.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "AWS Route53"},
        "search": [
            {"title": "Datadog - Cloud Scale Monitoring & Security", "url": "https://datadoghq.com", "snippet": "Datadog is the monitoring and security platform for cloud applications. We provide full-stack observability with SaaS tiered subscription licensing."},
            {"title": "Datadog About Us & Scale", "url": "https://datadoghq.com/about", "snippet": "Datadog has grown to over 5,500 employees globally serving thousands of enterprises."},
            {"title": "Datadog Tech Stack & LLM Monitoring", "url": "https://datadoghq.com/blog/llm-observability", "snippet": "Built on Go, Python, Kafka, and Kubernetes; launched LLM Observability module for AI workloads in late 2023."},
            {"title": "Datadog News & Expansion", "url": "https://datadoghq.com/news/expansion", "snippet": "Expansion triggers include launching cloud security management and growing government public sector contracts."},
        ],
        "scrape": {
            "https://datadoghq.com": "# Datadog Observability\nDatadog delivers infrastructure monitoring, application performance monitoring (APM), and log management via unified SaaS subscriptions.",
            "https://datadoghq.com/about": "# Company Scale\nDatadog employs more than 5,500 people in over 30 countries.",
            "https://datadoghq.com/blog/llm-observability": "# Tech Stack\nOur platform leverages Go microservices, Python, Apache Kafka, Cassandra, and Kubernetes orchestration.",
            "https://datadoghq.com/news/expansion": "# Sales Triggers\nDatadog announced Federal FedRAMP High Authorization and expansion of regional security engineering hubs.",
        }
    },
    "stripe.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "DNS Made Easy"},
        "search": [
            {"title": "Stripe - Financial Infrastructure for the Internet", "url": "https://stripe.com", "snippet": "Stripe builds economic infrastructure for the internet, monetizing via transaction fee percentages per processed payment and billing subscriptions."},
            {"title": "Stripe Company Size and Scale", "url": "https://stripe.com/about", "snippet": "Stripe has over 8,000 employees globally with dual headquarters in San Francisco and Dublin."},
            {"title": "Stripe Tech & Architecture", "url": "https://stripe.com/blog/ruby-sorbet-tech", "snippet": "Stripe's core services run on Ruby (Sorbet), Go, Java, and AWS infrastructure, with recent updates in AI-powered Radar fraud prevention."},
            {"title": "Stripe Market Triggers", "url": "https://stripe.com/newsroom/enterprise", "snippet": "Key triggers include enterprise migrations from legacy merchant gateways and rollout of crypto/stablecoin pay-ins."},
        ],
        "scrape": {
            "https://stripe.com": "# Stripe Payments Infrastructure\nMillions of companies use Stripe to accept payments, send payouts, and manage their businesses online with per-transaction fee economics.",
            "https://stripe.com/about": "# Stripe About\nOver 8,000 employees worldwide supporting hundreds of billions in annual transaction volume.",
            "https://stripe.com/blog/ruby-sorbet-tech": "# Technology\nUtilizes Ruby with static typing (Sorbet), Go microservices, Envoy, and AWS global infrastructure.",
            "https://stripe.com/newsroom/enterprise": "# Enterprise Expansion\nStripe announced enterprise partnerships with major global retail brands and expansion into Latin American payment methods.",
        }
    },
    "cloudflare.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare Internal DNS"},
        "search": [
            {"title": "Cloudflare - Connectivity Cloud", "url": "https://cloudflare.com", "snippet": "Cloudflare provides security, performance, and reliability solutions via global Anycast network on SaaS and enterprise contract models."},
            {"title": "Cloudflare Headcount", "url": "https://cloudflare.com/about", "snippet": "Cloudflare employs approximately 3,800 employees across 20+ offices worldwide."},
            {"title": "Cloudflare Workers AI Stack", "url": "https://cloudflare.com/products/workers-ai", "snippet": "Tech stack includes Rust, Go, C++, Linux kernel bypass, and Workers AI edge serverless runtime deployed across 300+ cities."},
            {"title": "Cloudflare Triggers", "url": "https://cloudflare.com/press/zero-trust", "snippet": "Key sales triggers: Zero Trust enterprise replacements, edge AI deployment, and DDoS mitigation for elections."},
        ],
        "scrape": {
            "https://cloudflare.com": "# Cloudflare Connectivity Cloud\nCloudflare protects and accelerates internet applications with SaaS subscriptions and custom enterprise pricing.",
            "https://cloudflare.com/about": "# About Cloudflare\nHeadquartered in San Francisco with over 3,800 employees globally.",
            "https://cloudflare.com/products/workers-ai": "# Edge Stack\nWorkers runtime running on V8 isolates, Rust, and NVIDIA GPUs at edge locations in 330 cities.",
            "https://cloudflare.com/press/zero-trust": "# Sales Triggers\nSurge in Zero Trust migrations from legacy VPN hardware and consolidation of cybersecurity vendors.",
        }
    },
    "hubspot.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "HubSpot - CRM Platform", "url": "https://hubspot.com", "snippet": "HubSpot offers an AI-powered customer platform with marketing, sales, and service software monetized on recurring SaaS tiers."},
            {"title": "HubSpot Company Size", "url": "https://hubspot.com/about", "snippet": "HubSpot employs over 7,500 employees globally with headquarters in Cambridge, MA."},
            {"title": "HubSpot Breeze AI Stack", "url": "https://hubspot.com/products/breeze", "snippet": "Announced Breeze AI suite built on Java, React, Kafka, and AWS microservices architecture."},
            {"title": "HubSpot Growth Triggers", "url": "https://hubspot.com/news/q2-expansion", "snippet": "Triggers include launching Breeze Copilot agents and upselling existing inbound marketing customers to Sales Hub Enterprise."},
        ],
        "scrape": {
            "https://hubspot.com": "# HubSpot Customer Platform\nIntegrated CRM, Marketing Hub, Sales Hub, and Service Hub on monthly/annual SaaS subscriptions.",
            "https://hubspot.com/about": "# About HubSpot\nOver 7,500 employees serving more than 200,000 customers worldwide.",
            "https://hubspot.com/products/breeze": "# Breeze AI Technology\nBuilt with Java, Python, React, and integrated with OpenAI and Google Gemini foundation models.",
            "https://hubspot.com/news/q2-expansion": "# Triggers\nAggressive shift into multi-hub enterprise accounts and international partner network expansion.",
        }
    },
    "shopify.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Shopify - Global Commerce Platform", "url": "https://shopify.com", "snippet": "Shopify powers multi-channel commerce with monthly subscription plans and merchant solutions transaction fees."},
            {"title": "Shopify Scale", "url": "https://shopify.com/about", "snippet": "Shopify has over 8,500 employees globally after restructuring into an agile product-focused organization."},
            {"title": "Shopify Tech Stack", "url": "https://shopify.com/engineering", "snippet": "Large-scale Ruby on Rails, React, GraphQL, React Native, and Google Cloud Platform infrastructure."},
            {"title": "Shopify Triggers", "url": "https://shopify.com/enterprise", "snippet": "Triggers include Shopify Plus enterprise expansion, B2B wholesale commerce, and international merchant localization."},
        ],
        "scrape": {
            "https://shopify.com": "# Shopify Commerce\nComplete commerce solution for DTC and B2B brands with subscription and merchant solutions revenue models.",
            "https://shopify.com/about": "# About Shopify\nOver 8,500 employees globally supporting millions of businesses in 175 countries.",
            "https://shopify.com/engineering": "# Engineering at Shopify\nPowered by Ruby on Rails, Storefront API in GraphQL, React, and Google Cloud Spanner.",
            "https://shopify.com/enterprise": "# Sales Triggers\nEnterprise brand wins migrating off SAP Hybris and Salesforce Commerce Cloud onto Shopify Plus.",
        }
    },
    "twilio.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Amazon Route53"},
        "search": [
            {"title": "Twilio - Customer Engagement Communications", "url": "https://twilio.com", "snippet": "Twilio offers APIs for SMS, voice, video, and Segment customer data platform with usage-based per-message pricing."},
            {"title": "Twilio Headcount", "url": "https://twilio.com/company", "snippet": "Twilio employs around 5,800 employees globally."},
            {"title": "Twilio Segment AI Stack", "url": "https://twilio.com/blog/customerai", "snippet": "Tech stack includes Java, Scala, Python, Kubernetes, AWS, and CustomerAI predictive features."},
            {"title": "Twilio Sales Triggers", "url": "https://twilio.com/press/enterprise", "snippet": "Key triggers include CustomerAI rollout, enterprise contact center automation, and cost rationalization initiatives."},
        ],
        "scrape": {
            "https://twilio.com": "# Twilio Communications API\nProgrammable Voice, Messaging, and Segment CDP with pay-as-you-go API consumption.",
            "https://twilio.com/company": "# About Twilio\nHeadquartered in San Francisco with 5,800+ employees globally.",
            "https://twilio.com/blog/customerai": "# Technology\nCustomerAI combining real-time data streaming on Kafka with generative AI models.",
            "https://twilio.com/press/enterprise": "# Triggers\nFocus on profitable growth and enterprise contact center modernization.",
        }
    },
    "atlassian.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Atlassian - Team Collaboration Software", "url": "https://atlassian.com", "snippet": "Atlassian develops Jira, Confluence, Loom, and Trello with recurring per-seat cloud SaaS subscriptions."},
            {"title": "Atlassian Scale", "url": "https://atlassian.com/company", "snippet": "Atlassian has over 11,000 employees globally with a remote-first 'Team Anywhere' work policy."},
            {"title": "Atlassian Rovo & Cloud Stack", "url": "https://atlassian.com/software/rovo", "snippet": "Launched Atlassian Rovo AI agentic search; stack built on Java, React, AWS, GraphQL, and Python."},
            {"title": "Atlassian Triggers", "url": "https://atlassian.com/press/cloud-migration", "snippet": "End of Server support driving massive enterprise migrations to Atlassian Cloud Enterprise."},
        ],
        "scrape": {
            "https://atlassian.com": "# Atlassian Software\nJira, Confluence, Loom, Bitbucket empowering agile software teams with per-seat licensing.",
            "https://atlassian.com/company": "# About Atlassian\nOver 11,000 employees across Australia, US, Europe, and Asia.",
            "https://atlassian.com/software/rovo": "# Atlassian Rovo\nAI agents utilizing Knowledge Graph and enterprise search across enterprise SaaS tools.",
            "https://atlassian.com/press/cloud-migration": "# Sales Triggers\nForced cloud migrations following Server license sunset and enterprise consolidation of ITSM tools.",
        }
    },
    "gitlab.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "GitLab - The DevSecOps Platform", "url": "https://gitlab.com", "snippet": "GitLab is an all-in-one DevSecOps platform with SaaS and self-managed tiered subscription revenue (Premium and Ultimate)."},
            {"title": "GitLab Scale", "url": "https://about.gitlab.com/company", "snippet": "GitLab is an all-remote company with approximately 2,200 team members in more than 65 countries."},
            {"title": "GitLab Duo AI Architecture", "url": "https://about.gitlab.com/solutions/ai", "snippet": "Tech stack features Ruby on Rails, Go, Vue.js, PostgreSQL, and GitLab Duo AI features powered by Anthropic and Vertex AI."},
            {"title": "GitLab Triggers", "url": "https://about.gitlab.com/press/q1-growth", "snippet": "Adoption of GitLab Duo AI add-ons and consolidation of security tools into single DevSecOps licensing."},
        ],
        "scrape": {
            "https://gitlab.com": "# GitLab DevSecOps\nComplete software development lifecycle from planning to CI/CD and security with per-seat SaaS subscriptions.",
            "https://about.gitlab.com/company": "# About GitLab\nAll-remote company with 2,200+ team members globally.",
            "https://about.gitlab.com/solutions/ai": "# GitLab Duo\nAI-assisted workflows built into the IDE and web platform using Go and Python backends.",
            "https://about.gitlab.com/press/q1-growth": "# Sales Triggers\nSecurity compliance mandates and toolchain consolidation driving upgrades to Ultimate tier.",
        }
    },
    "asana.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Asana - Work Management Platform", "url": "https://asana.com", "snippet": "Asana helps teams orchestrate their work from daily tasks to strategic initiatives with monthly/annual SaaS tiers."},
            {"title": "Asana Size & Team", "url": "https://asana.com/about", "snippet": "Asana employs roughly 1,700 employees with headquarters in San Francisco."},
            {"title": "Asana Intelligence & Tech", "url": "https://asana.com/product/ai", "snippet": "Built on TypeScript, React, Scala, Python, and AWS; features Asana Intelligence for automated workflow rules."},
            {"title": "Asana Market Triggers", "url": "https://asana.com/press/enterprise", "snippet": "Triggers include enterprise executive reporting adoption and competitive displacements of legacy spreadsheets."},
        ],
        "scrape": {
            "https://asana.com": "# Asana Work Management\nCross-functional project tracking and enterprise portfolio management with per-user subscription plans.",
            "https://asana.com/about": "# About Asana\nOver 1,700 employees globally serving 150,000+ paying organizations.",
            "https://asana.com/product/ai": "# Asana Intelligence\nWork graph data model powering AI smart summaries and workflow automations in TypeScript and Scala.",
            "https://asana.com/press/enterprise": "# Sales Triggers\nExpansion of Enterprise tier with stricter SOC2/HIPAA compliance and IT governance capabilities.",
        }
    },

    # 8 Mid-market SaaS / Software Houses
    "monterail.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Google Cloud DNS"},
        "search": [
            {"title": "Monterail - Web & Mobile Software House", "url": "https://monterail.com", "snippet": "Monterail is a full-service software development agency offering custom web and mobile app development on time-and-materials contracts."},
            {"title": "Monterail Team & Scale", "url": "https://monterail.com/about", "snippet": "Monterail has a team of 160+ developers, designers, and project managers based in Poland."},
            {"title": "Monterail Tech Stack", "url": "https://monterail.com/services", "snippet": "Core technologies include Ruby on Rails, Python, Vue.js, React, Node.js, and AWS cloud solutions."},
            {"title": "Monterail Triggers", "url": "https://monterail.com/blog/ai-services", "snippet": "Recent triggers include expanding Generative AI consulting services and hiring senior cloud architects."},
        ],
        "scrape": {
            "https://monterail.com": "# Monterail Software Development\nCustom web and mobile products for fintech, medtech, and e-commerce on T&M and dedicated team models.",
            "https://monterail.com/about": "# About Monterail\nOver 160 specialists delivering digital products since 2010.",
            "https://monterail.com/services": "# Technologies\nVue.js Official Partner, Ruby on Rails, Python, React Native, and AWS DevOps.",
            "https://monterail.com/blog/ai-services": "# Triggers\nLaunch of dedicated GenAI discovery workshops and growth in US/DACH client engagements.",
        }
    },
    "netguru.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Netguru - Digital Acceleration Consultancy", "url": "https://netguru.com", "snippet": "Netguru designs and builds digital solutions for startups and Fortune 500 enterprises with consulting and engineering fee structures."},
            {"title": "Netguru Scale & Employees", "url": "https://netguru.com/about-us", "snippet": "Netguru employs around 600 experts across Europe."},
            {"title": "Netguru Technologies", "url": "https://netguru.com/tech-stack", "snippet": "Stack includes React, Node.js, Python, Ruby on Rails, Flutter, and cloud-native Kubernetes environments."},
            {"title": "Netguru Sales Triggers", "url": "https://netguru.com/news/transformation", "snippet": "Key triggers include enterprise digital transformation projects and European green-tech consulting expansion."},
        ],
        "scrape": {
            "https://netguru.com": "# Netguru Digital Consultancy\nEngineering digital products with agile delivery teams and advisory services.",
            "https://netguru.com/about-us": "# Scale\nCertified B Corp with over 600 consultants and engineers across Europe.",
            "https://netguru.com/tech-stack": "# Tech Stack\nReact, React Native, Node.js, Python, Swift, Kotlin, and AWS/GCP cloud platforms.",
            "https://netguru.com/news/transformation": "# Triggers\nAccelerating AI adoption for banking clients and expanding sustainability practice.",
        }
    },
    "10clouds.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "10Clouds - AI & Software Development", "url": "https://10clouds.com", "snippet": "10Clouds builds AI-powered web and mobile applications for global startups and enterprises via dedicated engineering teams."},
            {"title": "10Clouds Team Size", "url": "https://10clouds.com/about", "snippet": "10Clouds has over 150 software engineers, UX designers, and AI specialists."},
            {"title": "10Clouds AI Stack", "url": "https://10clouds.com/services/ai", "snippet": "Specialized in LangChain, LlamaIndex, OpenAI API, Python, PyTorch, React, and Flutter."},
            {"title": "10Clouds Triggers", "url": "https://10clouds.com/blog/genai-studio", "snippet": "Launched dedicated AI Studio and partnership programs for seed/Series A startups."},
        ],
        "scrape": {
            "https://10clouds.com": "# 10Clouds AI Agency\nSpecialized software and AI development partner for fast-growing companies.",
            "https://10clouds.com/about": "# Team\n150+ engineers and designers delivering projects worldwide.",
            "https://10clouds.com/services/ai": "# AI Stack\nPython, PyTorch, LangChain, vector databases (Pinecone/Qdrant), and modern frontend frameworks.",
            "https://10clouds.com/blog/genai-studio": "# Triggers\nExpansion of enterprise LLM fine-tuning offerings and hiring AI research leads.",
        }
    },
    "brainly.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Brainly - Learning Community & AI Tutor", "url": "https://brainly.com", "snippet": "Brainly operates an online peer-to-peer learning network monetized via freemium Brainly Plus subscriptions and ads."},
            {"title": "Brainly Scale & Headcount", "url": "https://brainly.com/about", "snippet": "Brainly has over 350 employees and serves over 300 million monthly students and parents."},
            {"title": "Brainly AI Stack", "url": "https://brainly.com/engineering", "snippet": "Tech stack includes Python, Kotlin, Swift, React, GraphQL, and customized LLM Math tutoring models."},
            {"title": "Brainly Triggers", "url": "https://brainly.com/press/ai-tutor", "snippet": "Launch of AI Tutor features and monetization push into US school districts."},
        ],
        "scrape": {
            "https://brainly.com": "# Brainly EdTech Platform\nCrowdsourced homework assistance enhanced with personalized AI tutoring and premium subscription tiers.",
            "https://brainly.com/about": "# Company Size\n350+ employees headquartered in Kraków, Poland and New York City.",
            "https://brainly.com/engineering": "# Technology\nMicroservices on Kubernetes, Python ML models, GraphQL gateway, React Native mobile apps.",
            "https://brainly.com/press/ai-tutor": "# Sales Triggers\nRollout of Brainly Tutor with step-by-step AI explanation and expansion in Latin America.",
        }
    },
    "docplanner.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Docplanner - Healthcare Booking SaaS", "url": "https://docplanner.com", "snippet": "Docplanner provides SaaS practice management software for doctors and clinics alongside a patient booking marketplace."},
            {"title": "Docplanner Scale", "url": "https://docplanner.com/about", "snippet": "Docplanner has over 2,800 employees across offices in Poland, Spain, Italy, Brazil, and Mexico."},
            {"title": "Docplanner Stack", "url": "https://docplanner.com/tech", "snippet": "PHP/Symfony, TypeScript, React, Go, AWS, and AI phone receptionist integrations for clinics."},
            {"title": "Docplanner Triggers", "url": "https://docplanner.com/news/telemedicine", "snippet": "Recent M&A acquisitions of clinic management tools in Latin America and AI assistant rollout."},
        ],
        "scrape": {
            "https://docplanner.com": "# Docplanner Health Platform\nEmpowering medical practices with appointment scheduling, EHR software, and patient acquisition.",
            "https://docplanner.com/about": "# About Us\n2,800+ employees in 7 countries serving 80M+ patients monthly.",
            "https://docplanner.com/tech": "# Tech Architecture\nSymfony PHP, Go microservices, TypeScript, AWS Aurora, and automated WhatsApp appointment reminders.",
            "https://docplanner.com/news/telemedicine": "# Triggers\nAcquisitions in LATAM and launching AI phone agents to eliminate clinic missed calls.",
        }
    },
    "posthog.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "PostHog - All-in-one Product Analytics", "url": "https://posthog.com", "snippet": "PostHog is an open-source product analytics suite with product analytics, session recording, feature flags, and data warehouse on usage billing."},
            {"title": "PostHog Team", "url": "https://posthog.com/handbook/company/team", "snippet": "PostHog is an all-remote company with approximately 60 team members with transparent salaries."},
            {"title": "PostHog Tech Stack", "url": "https://posthog.com/handbook/engineering", "snippet": "Built on ClickHouse, Django/Python, TypeScript, React, Kafka, and Rust data capture ingest."},
            {"title": "PostHog Triggers", "url": "https://posthog.com/blog/data-warehouse", "snippet": "Launched managed Customer Data Platform (CDP) and native ClickHouse-powered data warehouse."},
        ],
        "scrape": {
            "https://posthog.com": "# PostHog Product Suite\nProduct analytics, web analytics, session replay, and feature flags with transparent usage pricing.",
            "https://posthog.com/handbook/company/team": "# Team & Culture\n60+ people working remotely across North America and Europe.",
            "https://posthog.com/handbook/engineering": "# Technology Stack\nClickHouse column-store database, Python Django backend, Rust ingestion pipeline, React frontend.",
            "https://posthog.com/blog/data-warehouse": "# Triggers\nHigh developer adoption replacing Mixpanel/Amplitude and expanding into enterprise self-hosted contracts.",
        }
    },
    "supabase.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Supabase - Open Source Firebase Alternative", "url": "https://supabase.com", "snippet": "Supabase provides Postgres database, authentication, instant APIs, edge functions, and vector embeddings on usage/tier SaaS pricing."},
            {"title": "Supabase Scale", "url": "https://supabase.com/about", "snippet": "Supabase is a remote-first team of over 100 developers and open source contributors worldwide."},
            {"title": "Supabase Tech Stack", "url": "https://supabase.com/blog/stack", "snippet": "PostgreSQL core, Elixir (Realtime), Go (auth/storage), Deno (Edge Functions), TypeScript, and pgvector."},
            {"title": "Supabase Triggers", "url": "https://supabase.com/press/ga", "snippet": "Announced General Availability (GA) and enterprise SLAs for mission-critical production workloads."},
        ],
        "scrape": {
            "https://supabase.com": "# Supabase Platform\nPostgres-based backend platform for developers with auth, database, realtime, and storage.",
            "https://supabase.com/about": "# About Supabase\n100+ team members across 30+ countries managing over 1 million registered databases.",
            "https://supabase.com/blog/stack": "# Architecture\nBuilt on native Postgres, Elixir Realtime server, Go GoTrue auth, and pgvector AI extension.",
            "https://supabase.com/press/ga": "# Triggers\nLarge enterprise migration from Firebase and AWS DynamoDB to managed Postgres.",
        }
    },
    "basecamp.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Amazon Route53"},
        "search": [
            {"title": "Basecamp - Project Management & Team Communication", "url": "https://basecamp.com", "snippet": "Basecamp by 37signals provides all-in-one project management and team collaboration with flat monthly pricing per company."},
            {"title": "Basecamp Scale & Employees", "url": "https://37signals.com/about", "snippet": "37signals/Basecamp employs approximately 80 employees in an intentional, profitable small-company model."},
            {"title": "Basecamp Tech Stack", "url": "https://37signals.com/technology", "snippet": "Creators of Ruby on Rails, Hotwire (Turbo/Stimulus), MySQL, Kamal deployment tool, and bare-metal servers."},
            {"title": "Basecamp Triggers", "url": "https://world.hey.com/dhh/cloud-exit", "snippet": "Saved millions leaving public cloud for bare-metal datacenter infrastructure and launched ONCE self-hosted software."},
        ],
        "scrape": {
            "https://basecamp.com": "# Basecamp\nProject management software with to-dos, message boards, schedules, and group chat on transparent flat pricing.",
            "https://37signals.com/about": "# About 37signals\n80 people company famous for books Rework, Remote, and bootstrapped profitability.",
            "https://37signals.com/technology": "# Technology Stack\nRuby on Rails, Hotwire (Turbo/Stimulus), Docker, Kamal, and self-hosted datacenter hardware.",
            "https://world.hey.com/dhh/cloud-exit": "# Triggers\nOngoing crusade on cloud exit cost savings and introduction of the ONCE non-subscription software suite.",
        }
    },

    # 4 Small / Local SMBs
    "boldare.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Boldare - Digital Product Design & Dev", "url": "https://boldare.com", "snippet": "Boldare designs and builds digital MVPs and SaaS platforms with agile scrum teams on time-and-materials billing."},
            {"title": "Boldare Headcount", "url": "https://boldare.com/about", "snippet": "Boldare employs around 130 digital product builders operating with holacracy."},
            {"title": "Boldare Tech Stack", "url": "https://boldare.com/technologies", "snippet": "React, Node.js, Python, TypeScript, GraphQL, AWS, and serverless architectures."},
            {"title": "Boldare Triggers", "url": "https://boldare.com/news/expansion", "snippet": "Expansion into European energy transition tech and medtech product discovery."},
        ],
        "scrape": {
            "https://boldare.com": "# Boldare Digital Products\nAgile product development partner helping companies launch MVPs and scale platforms.",
            "https://boldare.com/about": "# Team\n130+ designers and developers in Gliwice, Warsaw, and remote.",
            "https://boldare.com/technologies": "# Tech Stack\nTypeScript, React, Node.js, Python, serverless AWS, and Figma design systems.",
            "https://boldare.com/news/expansion": "# Triggers\nFocus on sustainability/cleantech software projects and AI product prototyping.",
        }
    },
    "droptica.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "OVH"},
        "search": [
            {"title": "Droptica - Drupal & PHP Web Agency", "url": "https://droptica.com", "snippet": "Droptica provides enterprise Drupal website development, maintenance, and support services on hourly and retainer contracts."},
            {"title": "Droptica Scale", "url": "https://droptica.com/company", "snippet": "Droptica has a team of 45+ Drupal and Symfony specialists based in Poland."},
            {"title": "Droptica Tech Stack", "url": "https://droptica.com/services/drupal", "snippet": "Drupal 10, PHP, Symfony, Docker, Linux, Apache/Nginx, and React headless integrations."},
            {"title": "Droptica Triggers", "url": "https://droptica.com/blog/drupal-10-migration", "snippet": "Surge in Drupal 7 end-of-life migrations to Drupal 10 for universities and corporate clients."},
        ],
        "scrape": {
            "https://droptica.com": "# Droptica Drupal Agency\nCustom Drupal portals, multisite management, and 24/7 technical support.",
            "https://droptica.com/company": "# Company\n45+ software engineers and Drupal certified architects in Wrocław and remote.",
            "https://droptica.com/services/drupal": "# Technologies\nDrupal 10, Symfony PHP, MySQL, Solr search, and decoupled frontends in React.",
            "https://droptica.com/blog/drupal-10-migration": "# Triggers\nMajor migration contracts due to Drupal 7 security end-of-life.",
        }
    },
    "apptension.com": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Apptension - Creative Software House", "url": "https://apptension.com", "snippet": "Apptension crafts web and mobile apps, creative websites, and SaaS MVPs with project-based and dedicated team contracts."},
            {"title": "Apptension Scale", "url": "https://apptension.com/about", "snippet": "Apptension employs roughly 50 specialists based in Poznań, Poland."},
            {"title": "Apptension Tech Stack", "url": "https://apptension.com/tech", "snippet": "Python, Django, React, Three.js/WebGL, AWS, and serverless microservices."},
            {"title": "Apptension Triggers", "url": "https://apptension.com/news/ai-accelerator", "snippet": "Launch of SaaS boilerplate accelerator with built-in AI capabilities for startup founders."},
        ],
        "scrape": {
            "https://apptension.com": "# Apptension Software Studio\nCreative digital experiences and SaaS development for international brands and startups.",
            "https://apptension.com/about": "# Team\n50+ developers, QA engineers, and creative producers.",
            "https://apptension.com/tech": "# Tech Stack\nReact, TypeScript, Three.js, Python/Django, AWS Lambda, Docker.",
            "https://apptension.com/news/ai-accelerator": "# Triggers\nNew product studio initiatives and expanding design sprint offerings.",
        }
    },
    "ideamotive.co": {
        "dns": {"has_mx": True, "has_a": True, "provider": "Cloudflare"},
        "search": [
            {"title": "Ideamotive - Tech Talent & Product Agency", "url": "https://ideamotive.co", "snippet": "Ideamotive connects companies with vetted software developers and builds custom web apps via staff augmentation and project delivery models."},
            {"title": "Ideamotive Scale", "url": "https://ideamotive.co/about", "snippet": "Ideamotive has a core team of ~30 people managing a network of 500+ vetted contractors."},
            {"title": "Ideamotive Tech Stack", "url": "https://ideamotive.co/technologies", "snippet": "Ruby on Rails, React, Node.js, Python, Flutter, and AI engineering."},
            {"title": "Ideamotive Triggers", "url": "https://ideamotive.co/insights/nearshoring", "snippet": "Growth in US tech companies hiring nearshore Eastern European engineering talent."},
        ],
        "scrape": {
            "https://ideamotive.co": "# Ideamotive Talent Network\nOn-demand software engineering teams and custom digital product consulting.",
            "https://ideamotive.co/about": "# Company\n30 core team members, 500+ vetted tech professionals network.",
            "https://ideamotive.co/technologies": "# Tech Capabilities\nReact, Node.js, Ruby on Rails, AWS, Python, and mobile cross-platform.",
            "https://ideamotive.co/insights/nearshoring": "# Triggers\nIncreased demand for AI/ML specialized contractors from North American SaaS firms.",
        }
    },

    # 3 Adversarial / Phantom / Stealth companies (Zero results, nonexistent domains)
    "omnivortexhypertech.nonexistent": {
        "dns": {"has_mx": False, "has_a": False, "provider": None, "error": "NXDOMAIN: Domain does not exist"},
        "search": [],
        "scrape": {}
    },
    "aetheriaquantumbio.invalid": {
        "dns": {"has_mx": False, "has_a": False, "provider": None, "error": "NXDOMAIN: Domain does not exist"},
        "search": [],
        "scrape": {}
    },
    "nonexistentphantomcorp123.fake": {
        "dns": {"has_mx": False, "has_a": False, "provider": None, "error": "NXDOMAIN: Domain does not exist"},
        "search": [],
        "scrape": {}
    }
}
