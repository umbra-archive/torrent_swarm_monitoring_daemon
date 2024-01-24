from tracker_scraper import scrape
r = scrape(
  tracker='udp://exodus.desync.com:6969',
  hashes=[
    "ff0bcba08ef0886a512032c037e6b065d9c5c458",
    "b73676a3d32a59a88e35eab35ab271900be60303",
    "c9b9f8bf46913bb2f89294fed74c2dd879f9acef",
    "9bf8c28967e481df5585291510550ef354ea91ec"
  ]
)


print(r)
