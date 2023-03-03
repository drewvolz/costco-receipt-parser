import subprocess

new_usage = subprocess.run(['python3', '-m', 'costcoparser', '-h'], capture_output=True, text=True).stdout.strip('\n')

start = ('<!--- START USAGE -->\n' '```shell script\n')
end = ('\n```\n' '<!--- END USAGE -->\n')

contents = ''

with open('README.md', 'r') as file:
	contents = file.read()

old_usage = contents[contents.find(start) + len(start):contents.rfind(end)]

contents = contents.replace(old_usage, new_usage)

with open('README.md', 'w') as file:
	file.write(contents)
