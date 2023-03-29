#!/home/ec2-user/anaconda3/envs/discord-bot/bin/python3
import commands_tree
import config as cfg

cfg.myclient.run(cfg.botutil.get_environvar("TOKEN"))
