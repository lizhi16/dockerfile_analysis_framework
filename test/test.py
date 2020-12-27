import crawl
import parse2cmds

dockerfile = crawl.resolve_images_info('cloudinsky/webserver')


print (parse2cmds.parse_dockerfile(dockerfile))
