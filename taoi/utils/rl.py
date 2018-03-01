try:
    import rlcompleter
    import readline
    readline.parse_and_bind("tab: complete")
except:
    print 'error enabling tab completion'
