/*
 * Source file:
 *	output.c
 *
 * Contains the formatting and output functions.
 */

#include "config.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "trueprint.h"
#include "main.h"
#include "diffs.h"
#include "headers.h"
#include "index.h"
#include "postscript.h"
#include "language.h"
#include "print_prompt.h"
#include "debug.h"
#include "options.h"
#include "utils.h"

#include "output.h"

/******************************************************************************
 * Public part
 */
long	file_page_number;
long	page_number;

/******************************************************************************
 * Private part
 */

typedef enum {
  INSERT,
  DELETE,
  NORMAL
} diff_states;

static void	add_char(short position,char character,char_status status,char *line,char_status line_status[]);
static int	line_end(char *input_line, int last_char_printed);
static stream_status printnextline(void);
static boolean	blank_page(boolean print_page);

/*
 * Local variables
 */
static boolean	no_clever_wrap;
static short	min_line_length;
static short	tabsize;
static boolean	no_function_page_breaks;
static boolean	new_sheet_after_file;
static boolean	no_expand_page_break;
static long	line_number;
static boolean	reached_end_of_sheet;

static char *segment_ends[4][3] = {
  /*     INSERT               DELETE             NORMAL       */
  /* NORMAL */    { ") BF setfont show ",   ") CF setfont So show ",   ") CF setfont show " },
		  /* ITALIC */    { ") IF setfont Bs ",     ") IF setfont So show ",   ") IF setfont show " },
		  /* BOLD */      { ") BF setfont show ",   ") BF setfont So show ",   ") BF setfont show " },
		  /* UNDERLINE */ { ") BF setfont Ul show", ") CF setfont So Ul show ",") CF setfont Ul show " },
};

/******************************************************************************
 * Function:
 *	init_output
 */
void
init_output(void)
{
  line_number = 0;
  page_number = 0;
}

/******************************************************************************
 * Function:
 *	setup_output
 */
void
setup_output(void)
{
  boolean_option("b", "no-page-break-after-function", "page-break-after-function", TRUE, &no_function_page_breaks, NULL, NULL,
		 OPT_TEXT_FORMAT,
		 "don't print page breaks at the end of functions",
		 "print page breaks at the end of functions");

  boolean_option(NULL, "new-sheet-after-file", "no-new-sheet-after-file", TRUE, &new_sheet_after_file, NULL, NULL, OPT_TEXT_FORMAT,
		 "Print each file on a new sheet of paper",
		 "Don't print each file on a new sheet of paper");

  boolean_option("W", "no-intelligent-line-wrap", "intelligent-line-wrap", FALSE, &no_clever_wrap, NULL, NULL,
		 OPT_TEXT_FORMAT,
		 "Wrap lines at exactly the line-wrap column",
		 "Wrap lines intelligently at significant characters, such\n"
		 "    as a space");

  short_option("L", "minimum-line-length", 10, NULL, 0, 5, 4096, &min_line_length, NULL, NULL,
	       OPT_TEXT_FORMAT, 
	       "minimum line length permitted by intelligent line wrap (default 10)",
	       NULL);
  short_option("T", "tabsize", 8, NULL, 0, 1, 20, &tabsize, NULL, NULL,
	       OPT_TEXT_FORMAT,
	       "set tabsize (default 8)", NULL);

  boolean_option("E", "ignore-form-feeds", "form-feeds", FALSE, &no_expand_page_break, NULL, NULL,
		 OPT_TEXT_FORMAT,
		 "don't expand form feed characters to new page",
		 "expand form feed characters to new page");
}