import setuptools
from distutils.core import setup

setup(
    name='MVAgentLauncher',
    packages=setuptools.find_packages(),
    version='1.0.0',
    description='A tool for management of MVAgent',
    author='Gennady O.',
    author_email='gennady.oren@mantis-vision.com',
    url='https://gitlab.com/gennady.oren/MVAgentLauncher',
    download_url='https://gitlab.com/gennady.oren/MVAgentLauncher',
    keywords=['python', 'easygui tools'],
    package_data={'MVAgentLauncher': ['kiosk_param.json','kiosk_nuc_param.json', 'MVAgentLauncher_start.bat','menu/*.txt','menu/*.png','menu/*.pdf']},
    include_package_data=True,
    classifiers=[],
    install_requires=['pypsexec', 'pywin32', 'requests'
    ],
    entry_points = {
        'console_scripts': ['MVAgentLauncher-tool = MVAgentLauncher.command_line:AgentLauncher'],
    }
)
