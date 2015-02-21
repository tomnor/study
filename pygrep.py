"""
Make a command line tool inspired by classic grep. The driver for doing so would
be that in case grepping a ms word file with the docx format, grep will
just say something match, but not display what is matched.

The reason for this is the binary format and maybe even more that the
file is some sort of compressed zip thing. Before grepping it one has to
unzip it. The unzipped files are of XML type. The line numbers in those
make no sense in relation to the outline as perceived by viewing the
document in the graphical application.

This tool then would display what is matched, but not attempt to give
any information on line numbers or context.
"""
