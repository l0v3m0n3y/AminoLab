from setuptools import setup, find_packages
setup(name='AminoLab.py',
      version='1.0',
      url = 'https://github.com/l0v3m0n3y/AminoLab',
    download_url = 'https://github.com/l0v3m0n3y/AminoLab/archive/refs/heads/main.zip',
      description='async libary for aminoapps.com. ton wallet: UQAeAZH2DkWqsU8zLtdpx9ELkM0agCtCoi8myYkPOJ-9ObNS',
      packages=['AminoLab.py'],
      author_email="pepsiritp@gmail.com",
      keywords = [
        'aminoapps',
        'amino-py',
        'amino',
        'amino-bot',
        'narvii',
        'api',
        'python',
        'python3',
        'python3.x',
        'botamino'
    ],
    install_requires = [
        'setuptools',
        'aiohttp',
    ],
    setup_requires = [
        'wheel'
    ]
)