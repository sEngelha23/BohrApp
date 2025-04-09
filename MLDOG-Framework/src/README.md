# Team 9



## Getting started

<<<<<<< HEAD
To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://git.hs-offenburg.de/ml/projekt-1/2024-winter/team-9.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://git.hs-offenburg.de/ml/projekt-1/2024-winter/team-9/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***


## Name
Vorhersage des gebohrten Materials

## Description
Das Projekt zielt darauf ab, ein System zu entwickeln, das anhand von Sensordaten (Akustik, Stromstärke und Spannung) während eines Bohrprozesses automatisch erkennt und vorhersagt, in welches Material gebohrt wurde. 
Durch den Einsatz von Machine Learning werden Muster in den Messwerten identifiziert, die charakteristisch für spezifische Materialien (Holz-Span, Kunststoff-POM) sind.


## Visuals
![Bild_01](h:\Semester_3\Projekt1\git_proj1\team-9\Bilder)

## Installation
Schauen Sie, dass Ihr Computer mindestens Python 3.10 Installiert hat. Falls das nicht der Fall ist installieren Sie es(https://www.python.org/downloads/).

## Starten des Programms
Öffnen Sie das linux Terminal gehen Sie mittels cd Befehl in den Ordner team-9 und die Unterordner MLDOG-Framework und src. 
Installieren Sie anschlißend die für das Programm erstellte Umgebung indem Sie im Terminal 'conda env create -f environment.yml' eingeben.
Danach müssen Sie die Umgebung noch activieren durch 'conda activate environment-team-9'.
Um die Benutzeroberfläche zu öffnen geben Sie 'python DrillOG.py' ein. Nun sehen Sie drei Bedienfelder, Sie nutzen das oberste namens 'UDP Data Source' und gelangen so zu vier weiteren Bedienfelder.
Zur Nutzung des Vorhersagemodell klicken Sie auf Vorhersage. Jetzt können Sie direkt mit Ihrer Bohrung starten.

## Usage
Zunächst öffnen Sie die GUI Oberfläche. Ein Bohrvorgang wird vom System automatisch erkannt. Anschließend werden die Daten, ebenfalls automatisch, an das Machine Learning Modell weitergeleitet. 
Das vortrainierte Modell trifft mit einer hohen Genauigkeit eine Vorhersage um welches Material es sich handelt. Die Vorhersage wird dann auf der GUI Oberfläche ausgegeben.

## Support
Bei Fragen, wenden Sie sich gerne bei einem Mitglied unseres Teams:
Elias Folwaczny: efolwacz@stud.hs-offenburg.de
Sebastian Engelhardt: sengelha@stud.hs-offenburg.de
Roland Kummer: rkummer1@stud.hs-offenburg.de
Ronja Österle: roesterl@stud.hs-offenburg.de

## Authors and acknowledgment
Erstellt von Elias Folwaczny, Sebastian Engelhardt, Roland Kummer und Ronja Österle. Vielen Dank an das gesammte Team, sowie an Herr Glaser und Frau Ölke.

## Project status
In bearbeitung...

<<<<<<< HEAD


>>>>>>>
=======
- **[DrillOG.py](DrillOG.py)**: Main-Funktion zum Starten der Demonstrator-Anwendung mit dem Bohrer Kontext.


## Environment
name: drill

channels:
  - defaults
  - conda-forge

dependencies:
  - python=3.12
  - jupyterlab
  - numpy
  - pandas
  - matplotlib
  - seaborn
  - plotly
  - plotly_express
  - scikit-learn = 1.5.1
  - tsfresh = 0.20.2


- ****
>>>>>>>