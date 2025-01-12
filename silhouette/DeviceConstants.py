
# taken from
#  robocut/CutDialog.ui
#  robocut/CutDialog.cpp

MEDIA = [
# CAUTION: keep in sync with sendto_silhouette.inx
# media, pressure, speed, depth, cap-color, name
  ( 300, None,   None,None,  "custom", "Custom"),
  ( 100,   27,     10,   1,  "yellow", "Card without Craft Paper Backing"),
  ( 101,   27,     10,   1,  "yellow", "Card with Craft Paper Backing"),
  ( 102,   10,      5,   1,  "blue",   "Vinyl Sticker"),
  ( 106,   14,     10,   1,  "blue",   "Film Labels"),
  ( 111,   27,     10,   1,  "yellow", "Thick Media"),
  ( 112,    2,     10,   1,  "blue",   "Thin Media"),
  ( 113,   18,     10,None,  "pen",    "Pen"),
  ( 120,   30,     10,   1,  "blue",   "Bond Paper 13-28 lbs (105g)"),
  ( 121,   30,     10,   1,  "yellow", "Bristol Paper 57-67 lbs (145g)"),
  ( 122,   30,     10,   1,  "yellow", "Cardstock 40-60 lbs (90g)"),
  ( 123,   30,     10,   1,  "yellow", "Cover 40-60 lbs (170g)"),
  ( 124,    1,     10,   1,  "blue",   "Film, Double Matte Translucent"),
  ( 125,    1,     10,   1,  "blue",   "Film, Vinyl With Adhesive Back"),
  ( 126,    1,     10,   1,  "blue",   "Film, Window With Kling Adhesive"),
  ( 127,   30,     10,   1,  "red",    "Index 90 lbs (165g)"),
  ( 128,   20,     10,   1,  "yellow", "Inkjet Photo Paper 28-44 lbs (70g)"),
  ( 129,   27,     10,   1,  "red",    "Inkjet Photo Paper 45-75 lbs (110g)"),
  ( 130,   30,      3,   1,  "red",    "Magnetic Sheet"),
  ( 131,   30,     10,   1,  "blue",   "Offset 24-60 lbs (90g)"),
  ( 132,    5,     10,   1,  "blue",   "Print Paper Light Weight"),
  ( 133,   25,     10,   1,  "yellow", "Print Paper Medium Weight"),
  ( 134,   20,     10,   1,  "blue",   "Sticker Sheet"),
  ( 135,   20,     10,   1,  "red",    "Tag 100 lbs (275g)"),
  ( 136,   30,     10,   1,  "blue",   "Text Paper 24-70 lbs (105g)"),
  ( 137,   30,     10,   1,  "yellow", "Vellum Bristol 57-67 lbs (145g)"),
  ( 138,   30,     10,   1,  "blue",   "Writing Paper 24-70 lbs (105g)"),
]

CAMEO_MATS = dict(
  no_mat=('0', False, False),
  cameo_12x12=('1', 12, 12),
  cameo_12x24=('2', 24, 12),
  portrait_8x12=('3', 12, 8),
  cameo_plus_15x15=('8', 15, 15),
  cameo_pro_24x24=('9', 24, 24)
)

#  robocut/Plotter.h:53 ff
VENDOR_ID_GRAPHTEC = 0x0b4d
PRODUCT_ID_CC200_20 = 0x110a
PRODUCT_ID_CC300_20 = 0x111a
PRODUCT_ID_SILHOUETTE_SD_1 = 0x111c
PRODUCT_ID_SILHOUETTE_SD_2 = 0x111d
PRODUCT_ID_SILHOUETTE_CAMEO =  0x1121
PRODUCT_ID_SILHOUETTE_CAMEO2 =  0x112b
PRODUCT_ID_SILHOUETTE_CAMEO3 =  0x112f
PRODUCT_ID_SILHOUETTE_CAMEO4 =  0x1137
PRODUCT_ID_SILHOUETTE_CAMEO4PLUS = 0x1138
PRODUCT_ID_SILHOUETTE_CAMEO4PRO = 0x1139
PRODUCT_ID_SILHOUETTE_CAMEO5 =  0x1140
PRODUCT_ID_SILHOUETTE_CAMEO5PLUS =  0x1141
PRODUCT_ID_SILHOUETTE_PORTRAIT = 0x1123
PRODUCT_ID_SILHOUETTE_PORTRAIT2 = 0x1132
PRODUCT_ID_SILHOUETTE_PORTRAIT3 = 0x113a

PRODUCT_LINE_CAMEO4 = [
  PRODUCT_ID_SILHOUETTE_CAMEO4,
  PRODUCT_ID_SILHOUETTE_CAMEO4PLUS,
  PRODUCT_ID_SILHOUETTE_CAMEO4PRO,
  PRODUCT_ID_SILHOUETTE_CAMEO5,  #Given the similarities between Cameo 4 and Cameo 5, I added Cameo 5 to this list
  PRODUCT_ID_SILHOUETTE_CAMEO5PLUS,  #Given the similarities between Cameo 4 and Cameo 5, I added Cameo 5 to this list
  PRODUCT_ID_SILHOUETTE_PORTRAIT3,
]

PRODUCT_LINE_CAMEO3_ON = PRODUCT_LINE_CAMEO4 + [PRODUCT_ID_SILHOUETTE_CAMEO3]
PRODUCTS_WITH_TWO_TOOLS = [p for p in PRODUCT_LINE_CAMEO3_ON if p != PRODUCT_ID_SILHOUETTE_PORTRAIT3]

# End Of Text - marks the end of a command
CMD_ETX = b'\x03'
# Escape - send escape command
CMD_ESC = b'\x1b'

### Escape Commands
# End Of Transmission - will initialize the device,
CMD_EOT = b'\x04'
# Enquiry - Returns device status
CMD_ENQ = b'\x05'
# Negative Acnoledge - Returns device tool setup
CMD_NAK = b'\x15'

### Query codes
QUERY_FIRMWARE_VERSION = b'FG'

### Response codes
RESP_READY    = b'0'
RESP_MOVING   = b'1'
RESP_UNLOADED = b'2'
RESP_DECODING = {
  RESP_READY:    'ready',
  RESP_MOVING:   'moving',
  RESP_UNLOADED: 'unloaded'
}

SILHOUETTE_CAMEO4_TOOL_EMPTY = 0
SILHOUETTE_CAMEO4_TOOL_RATCHETBLADE = 1
SILHOUETTE_CAMEO4_TOOL_AUTOBLADE = 2
SILHOUETTE_CAMEO4_TOOL_DEEPCUTBLADE = 3
SILHOUETTE_CAMEO4_TOOL_KRAFTBLADE = 4
SILHOUETTE_CAMEO4_TOOL_ROTARYBLADE = 5
SILHOUETTE_CAMEO4_TOOL_PEN = 7
SILHOUETTE_CAMEO4_TOOL_ERROR = 255

DEVICE = [
 # CAUTION: keep in sync with sendto_silhouette.inx
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_PORTRAIT, 'name': 'Silhouette_Portrait',
   'width_mm':  206, 'length_mm': 3000, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_PORTRAIT2, 'name': 'Silhouette_Portrait2',
   'width_mm':  203, 'length_mm': 3000, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_PORTRAIT3, 'name': 'Silhouette_Portrait3',
   'width_mm':  203, 'length_mm': 18290, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_CAMEO, 'name': 'Silhouette_Cameo',
   # margin_top_mm is just for safety when moving backwards with thin media
   # margin_left_mm is a physical limit, but is relative to width_mm!
   'width_mm':  304, 'length_mm': 3000, 'margin_left_mm':9.0, 'margin_top_mm':1.0, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_CAMEO2, 'name': 'Silhouette_Cameo2',
   # margin_top_mm is just for safety when moving backwards with thin media
   # margin_left_mm is a physical limit, but is relative to width_mm!
   'width_mm':  304, 'length_mm': 3000, 'margin_left_mm':0.0, 'margin_top_mm':0.0, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_CAMEO3, 'name': 'Silhouette_Cameo3',
   # margin_top_mm is just for safety when moving backwards with thin media
   # margin_left_mm is a physical limit, but is relative to width_mm!
   'width_mm':  304.8, 'length_mm': 3000, 'margin_left_mm':0.0, 'margin_top_mm':0.0, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_CAMEO4, 'name': 'Silhouette_Cameo4',
   # margin_top_mm is just for safety when moving backwards with thin media
   # margin_left_mm is a physical limit, but is relative to width_mm!
   'width_mm':  304.8, 'length_mm': 3000, 'margin_left_mm':0.0, 'margin_top_mm':0.0, 'regmark': True },
{ 'vendor_id': VENDOR_ID_GRAPHTEC,
  'product_id': PRODUCT_ID_SILHOUETTE_CAMEO4PLUS,
  'name': 'Silhouette_Cameo4_Plus',
  'width_mm': 372, # A bit of a guess, not certain what actual cuttable is (not sure what it is or how to test it)
  'length_mm': 3000,
  'margin_left_mm': 0.0, 'margin_top_mm': 0.0, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC,
   'product_id': PRODUCT_ID_SILHOUETTE_CAMEO4PRO,
   'name': 'Silhouette_Cameo4_Pro',
   'width_mm': 600, # 24 in. is 609.6mm, but Silhouette Studio shows a thin cut
                    # margin that leaves 600mm of cuttable width. However,
                    # I am not certain if this should be margin_left_mm = 4.8
                    # and width_mm = 604.8; trying to leave things as close to
                    # the prior Cameo4 settings above.
   'length_mm': 3000,
   'margin_left_mm': 0.0, 'margin_top_mm': 0.0, 'regmark': True },
   { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_CAMEO5, 'name': 'Silhouette_Cameo5',
   # Took these settings from Cameo 4, haven't noticed any performance issues.
   #added extra margin space to experiment with the software cross-cutting feature
   'width_mm':  330.2, 'length_mm': 3000, 'margin_left_mm': -6.0, 'margin_top_mm': 0.0, 'regmark': True },
   { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_CAMEO5PLUS, 'name': 'Silhouette_Cameo5_Plus',
   # Took these settings from Cameo 4 Plus, haven't noticed any performance issues.
   'width_mm':  372, 'length_mm': 3000, 'margin_left_mm': 0.0, 'margin_top_mm': 0.0, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_CC200_20, 'name': 'Craft_Robo_CC200-20',
   'width_mm':  200, 'length_mm': 1000, 'regmark': True },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_CC300_20, 'name': 'Craft_Robo_CC300-20' },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_SD_1, 'name': 'Silhouette_SD_1' },
 { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_SD_2, 'name': 'Silhouette_SD_2' },
]
