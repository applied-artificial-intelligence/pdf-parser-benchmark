# Creating Dialog Boxes

Dialog boxes may be created in one of two ways:

-  Using the function GetNewDialog, which takes descriptive information about the dialog from dialog ('DLOG') and extended dialog ('d1gx') resources. The resource ID of the ('DLog') and ('d1gx') resources must be the same, and is passed in the first parameter of this function.
-  Using NewDialog, NewColorDialog, or NewFeaturesDialog, which take descriptive information passed in the parameters of those functions.

# Historical Note

The extended dialog resource and the NewFeaturesDialog function were introduced with OS 8 and the Appearance Manager. NewFeaturesDialog should be used to create Appearance-compliant dialogs. Unlike NewDialog and NewColorDialog, it has a flags parameter containing the same flags you would set in an extended dialog resource.

If NULL is specified as the second parameter in the GetNewDialog call, GetNewDialog itself creates a nonrelocatable block for the dialog structure. Passing NULL is appropriate for modal and movable modal dialog boxes because you should dispose of the dialog box, and hence the associated dialog structure, when the user dismisses the dialog. However, in order to avoid heap fragmentation effects, you should ordinarily allocate your own memory for modeless dialog box dialog structures (just as you would for a window structure) and specify the pointer to that memory block in the second parameter of the GetNewDialog call.

Regardless of which method is used to create the dialog, a dialog structure and a window structure will be created, and a pointer to the dialog structure will be returned to the calling function.

# The Dialog Structure

The dialog structure created by the GetNewDialog call is defined by the data type DialogRecord:

struct DialogRecord
{
\tWindowRecord window;// Dialog's window record.
\tHandle item //Item list resource.
\tTEHandle   textH;    // Current editable text item.
\tSInt16 editField;// Editable text item number 1.
\tSInt16 editOpen; // (Used internally.)
\tSInt16 aDefItem;  // Default push button item number.
};
typedef struct DialogRecord DialogRecord;
typedef DialogRecord *DialogPeek;

Note that the dialog structure includes a window structure field. The Dialog Manager sets the windowkind field of this window structure to kDialogWindowKind.
