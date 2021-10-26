from rich.prompt import Confirm, Prompt

from wrapper.console.TUI import ExegolTUI
from wrapper.manager.GitManager import GitManager
from wrapper.utils.ConstantConfig import ConstantConfig
from wrapper.utils.DockerUtils import DockerUtils
from wrapper.utils.ExeLog import logger


class UpdateManager:
    __git = GitManager()

    @staticmethod
    def updateImage(tag=None):
        """User procedure to build/pull docker image"""
        # List Images
        images = DockerUtils.listImages()
        selected_image = None
        # Select image
        if tag is None:
            logger.info(images)
            # Interactive selection
            # TODO select image (need TUI)
            selected_image = images[0]
        else:
            # Find image by name
            for img in images:
                if img.getName() == tag:
                    selected_image = img
                    break

        if selected_image is not None:
            # Update
            DockerUtils.updateImage(selected_image)
        else:
            # Install / build image
            # Ask confirm to build ?
            raise NotImplementedError

    @classmethod
    def updateGit(cls):
        """User procedure to update local git repository"""
        # Check if pending change -> cancel
        if not cls.__git.safeCheck():
            logger.error("Aborting git update.")
            return
        # List & Select git branch
        selected_branch = ExegolTUI.selectFromList(cls.__git.listBranch(),
                                                   subject="a git branch",
                                                   title="Branch",
                                                   default=cls.__git.getCurrentBranch())
        # Checkout new branch
        if selected_branch is not None and selected_branch != cls.__git.getCurrentBranch():
            cls.__git.checkout(selected_branch)
        # git pull
        cls.__git.update()

    @classmethod
    def buildSource(cls):
        # Ask to update git
        if Confirm.ask("[blue][?][/blue] Do you want to update git?",
                       choices=["Y", "n"],
                       show_default=False,
                       default=True):
            cls.updateGit()
        # Choose tag name
        build_name = Prompt.ask("[blue][?][/blue] Choice a name for your build",
                                default="local")  # TODO add blacklist build name
        # Choose dockerfile
        build_profile = ExegolTUI.selectFromList(cls.__listBuildProfiles(),
                                                 subject="a build profile",
                                                 title="Profile",
                                                 default="stable")
        # Docker Build
        DockerUtils.buildImage(build_name, build_profile)

    @classmethod
    def __listBuildProfiles(cls):
        # Default stable profile
        profiles = {"stable": "Dockerfile"}
        # List file *.dockerfile is the build context directory
        docker_files = list(ConstantConfig.build_context_path_obj.glob("*.dockerfile"))
        for file in docker_files:
            # Convert every file to the dict format
            filename = file.name
            profile_name = filename.replace(".dockerfile", "")
            profiles[profile_name] = filename
        logger.debug(f"List docker build profiles : {profiles}")
        return profiles
