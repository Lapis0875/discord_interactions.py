from setuptools import setup, find_packages

with open('README.md', mode='rt', encoding='utf-8') as f:
    long_desc: str = f.read()


# Setup module
setup(
    # Module name
    name="discord_slash.py",
    # Module version
    version="1.0.0",
    # License - MIT!
    license='MIT',
    # Author (Github username)
    author="Lapis0875",
    # Author`s email.
    author_email="lapis0875@kakao.com",
    # Short description
    description="Python wrapper of Discord's Interactions API (a.k.a. Slash Commands)",
    # Long description in REAMDME.md
    long_description=long_desc,
    long_description_content_type='text/markdown',
    # Project urls
    project_urls={
        'Documentation': 'https://lapis0875.gitbook.io/discordSlashPy-docs/',
        'Source': 'https://github.com/Lapis0875/discord_slash.py/',
        'Tracker': 'https://github.com/Lapis0875/DiscordPyEmbed/issues/',
        'Funding': 'https://www.patreon.com/lapis0875'
    },
    # Include module directory
    packages=find_packages(),
    # Dependencies
    install_requires=["wheel>=0.36.2", "aiohttp>=3.6.3", "discord.py>=1.6.0"],
    # Module`s python requirement
    python_requires=">=3.5.3",
    # Keywords about the module
    keywords=["discord api", "discord.py", "discord slash command", "discord interactions api"],
    # Tags about the module
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
